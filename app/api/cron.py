from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.services.aggregate_service import aggregate_monthly, cleanup_old_logs

router = APIRouter(prefix="/cron", tags=["Cron"])


# ======================
# SECURITY (WAJIB)
# ======================
def verify_cron(x_cron_token: str = Header(None)):
    if x_cron_token != "SECRET_CRON_KEY":
        raise HTTPException(status_code=403, detail="Forbidden")


# ======================
# CRON ENDPOINT
# ======================
@router.post("/aggregate")
def run_aggregation(
    db: Session = Depends(get_db),
    _: str = Depends(verify_cron)
):

    now = datetime.now()

    # ambil bulan lalu
    if now.month == 1:
        year = now.year - 1
        month = 12
    else:
        year = now.year
        month = now.month - 1

    # ======================
    # 1. AGGREGATE
    # ======================
    aggregate_result = aggregate_monthly(db, year, month)

    # ======================
    # 2. CLEANUP LOGS
    # ======================
    cleanup_result = cleanup_old_logs(db, days=30)

    return {
        "aggregation": aggregate_result,
        "cleanup": cleanup_result
    }