import hashlib
import hmac
from fastapi import  Request, HTTPException, Header
from api_gateway.config import settings

import logging
logger = logging.getLogger(__name__)

async def verify_signature(request: Request, x_hub_signature_256: str = Header(None)):
    """Security: Ensure the request actually came from GitHub."""
    if not settings.WEBHOOK_SECRET:
        return # Skip if no secret configured (Dev mode)
    
    if not x_hub_signature_256:
        raise HTTPException(status_code=403, detail="Missing X-Hub-Signature-256 header")
    
    payload = await request.body()
    signature = "sha256=" + hmac.new(
        settings.WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")