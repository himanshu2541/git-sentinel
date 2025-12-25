import logging
import json
from fastapi import APIRouter, Request, Header
from shared.providers.redis import RedisFactory
from api_gateway.core.utils import verify_signature

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