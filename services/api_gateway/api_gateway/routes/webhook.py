import logging
import json
from fastapi import APIRouter, Request, Header, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from pydantic import BaseModel
from shared.providers.redis import RedisFactory
from api_gateway.core.utils import verify_signature
from api_gateway.config import settings

router = APIRouter()
logger = logging.getLogger("Gateway.Webhook")

@router.post("/github")
async def handle_github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    """
    1. Validates the webhook.
    2. Filters for 'pull_request' events.
    3. Pushes valid events to Redis for async processing.
    """
    await verify_signature(request, x_hub_signature_256)
    
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    # We only care about opened or synchronized (updated) PRs
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            job_data = {
                "repo_name": payload["repository"]["full_name"],
                "pr_number": payload["number"],
                "installation_id": payload.get("installation", {}).get("id")
            }
            
            # Push to Redis Queue for async processing
            redis = RedisFactory.get_client()
            await redis.lpush("review_jobs", json.dumps(job_data)) # type: ignore
            
            logger.info(f"Queued PR #{job_data['pr_number']} for {job_data['repo_name']}")
            return {"status": "queued"}

    return {"status": "ignored"}


class ManualReviewRequest(BaseModel):
    repo_name: str = "Manual-Override"
    code: str

@router.post("/manual")
async def manual_review_endpoint(payload: ManualReviewRequest):
    """
    Accepts raw code from Frontend and queues it for the Worker.
    """
    job_data = {
        "source": "manual",
        "code": payload.code,
        "repo_name": payload.repo_name,
        "pr_number": 0
    }
    
    redis = RedisFactory.get_client()
    await redis.lpush("review_jobs", json.dumps(job_data)) # type: ignore
    
    return {"status": "queued", "message": "Manual review started"}

    
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create a DEDICATED connection with NO timeout for this long-lived socket.
    # We cannot use the shared pool if it has a default timeout.
    redis_ws = Redis.from_url(settings.REDIS_URL, socket_timeout=None)
    pubsub = redis_ws.pubsub()
    
    await pubsub.subscribe("sentinel_events")
    logger.info("WebSocket connected and subscribed to Redis.")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Forward Redis message to Browser
                # Redis sends bytes, so we decode to string
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                    
                await websocket.send_text(data)
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
    finally:
        # Close the dedicated connection when the socket closes
        await pubsub.unsubscribe("sentinel_events")
        await redis_ws.close()