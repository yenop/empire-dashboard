from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import AppModel

router = APIRouter(prefix="/api/mrr", tags=["mrr"])


@router.get("", response_model=dict)
def mrr_summary(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    total = db.scalar(select(func.coalesce(func.sum(AppModel.mrr), 0)))
    return {
        "mrr_total": str(Decimal(str(total)) if total is not None else "0"),
        "currency": "USD",
        "source": "database",
    }
