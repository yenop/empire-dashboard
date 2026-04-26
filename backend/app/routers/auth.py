from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from passlib.context import CryptContext

from app.config import get_settings
from app.limiter import limiter
from app.schemas import LoginBody, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    body: LoginBody,
) -> TokenResponse:
    _ = request
    settings = get_settings()
    if not settings.empire_password_hash:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EMPIRE_PASSWORD_HASH is not set",
        )
    if body.username != settings.empire_auth_username:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not pwd_context.verify(body.password, settings.empire_password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.empire_jwt_expire_minutes
    )
    token = jwt.encode(
        {
            "sub": body.username,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        },
        settings.empire_jwt_secret,
        algorithm="HS256",
    )
    return TokenResponse(access_token=token, token_type="bearer")
