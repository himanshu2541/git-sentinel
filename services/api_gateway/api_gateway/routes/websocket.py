import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from shared.providers.redis import RedisFactory

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis = RedisFactory.get_client()
    pubsub = redis.pubsub()
    await pubsub.subscribe("sentinel_events")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Forward Redis message to Browser
                await websocket.send_text(message["data"].decode("utf-8"))
    except WebSocketDisconnect:
        await pubsub.unsubscribe("sentinel_events")