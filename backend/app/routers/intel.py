from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import IntelModel
from app.schemas import IntelItemOut

router = APIRouter(prefix="/api/intel", tags=["intel"])


@router.get("", response_model=list[IntelItemOut])
def list_intel(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[IntelItemOut]:
    rows = (
        db.scalars(select(IntelModel).order_by(IntelModel.created_at.desc()).limit(50))
        .all()
    )
    return [IntelItemOut.from_row(i) for i in rows]
