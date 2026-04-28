import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

http_bearer = HTTPBearer(auto_error=True)


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    settings = get_settings()
    if not settings.empire_jwt_secret:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT not configured",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.empire_jwt_secret,
            algorithms=["HS256"],
        )
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return sub
    except jwt.PyJWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_internal_api_key(
    x_empire_internal_key: str | None = Header(default=None, alias="X-Empire-Internal-Key"),
) -> None:
    settings = get_settings()
    expected = (settings.empire_internal_api_key or "").strip()
    if not expected:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API key not configured",
        )
    got = (x_empire_internal_key or "").strip()
    if not got or got != expected:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )
