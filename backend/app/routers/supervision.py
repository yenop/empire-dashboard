import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.deps import get_current_username

router = APIRouter(prefix="/api/supervision", tags=["supervision"])


@router.get("/openclaw")
async def openclaw_status(_username: str = Depends(get_current_username)):
    settings = get_settings()
    if not settings.openclaw_gateway_url or not settings.openclaw_gateway_token:
        return JSONResponse(
            status_code=200,
            content={
                "configured": False,
                "message": "Set OPENCLAW_GATEWAY_URL and OPENCLAW_GATEWAY_TOKEN to enable",
            },
        )
    base = settings.openclaw_gateway_url.rstrip("/")
    status_url = f"{base}/api/status"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                status_url,
                headers={"Authorization": f"Bearer {settings.openclaw_gateway_token}"},
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail="OpenClaw gateway unreachable",
        ) from e
    if r.status_code != 200:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail="OpenClaw returned an error",
        )
    try:
        payload = r.json()
    except Exception:
        payload = {"raw": r.text}
    return {"configured": True, "gateway": base, "status": payload}
