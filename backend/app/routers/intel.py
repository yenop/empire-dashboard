from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

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
        db.scalars(
            select(IntelModel)
            .options(joinedload(IntelModel.agent), joinedload(IntelModel.task))
            .order_by(IntelModel.created_at.desc())
            .limit(50)
        )
        .unique()
        .all()
    )
    return [IntelItemOut.from_row(i) for i in rows]
