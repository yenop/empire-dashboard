from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import AppModel
from app.schemas import AppOut

router = APIRouter(prefix="/api/apps", tags=["apps"])


@router.get("", response_model=list[AppOut])
def list_apps(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[AppOut]:
    rows = db.scalars(select(AppModel).order_by(AppModel.name)).all()
    return [AppOut.model_validate(r) for r in rows]


@router.get("/{app_id}", response_model=AppOut)
def get_app(
    app_id: str,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> AppOut:
    row = db.get(AppModel, app_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")
    return AppOut.model_validate(row)
