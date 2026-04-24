from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.models.incoming_log import IncomingLog
from app.models.outgoing_log import OutgoingLog
from app.models.monthly_summary import MonthlySummary


def aggregate_monthly(db: Session, year: int, month: int):

    # ======================
    # 1. DELETE OLD SUMMARY (ANTI DUPLICATE)
    # ======================
    db.query(MonthlySummary).filter(
        MonthlySummary.year == year,
        MonthlySummary.month == month
    ).delete()

    db.commit()

    # ======================
    # 2. AGGREGATE INCOMING
    # ======================
    incoming_data = db.query(
        IncomingLog.type_id,
        func.sum(IncomingLog.quantity).label("total")
    ).filter(
        extract("year", IncomingLog.created_at) == year,
        extract("month", IncomingLog.created_at) == month
    ).group_by(IncomingLog.type_id).all()

    # ======================
    # 3. AGGREGATE OUTGOING
    # ======================
    outgoing_data = db.query(
        OutgoingLog.type_id,
        func.sum(OutgoingLog.quantity).label("total")
    ).filter(
        extract("year", OutgoingLog.created_at) == year,
        extract("month", OutgoingLog.created_at) == month
    ).group_by(OutgoingLog.type_id).all()

    # ======================
    # 4. MAP DATA
    # ======================
    incoming_map = {i.type_id: int(i.total) for i in incoming_data}
    outgoing_map = {o.type_id: int(o.total) for o in outgoing_data}

    all_type_ids = set(incoming_map.keys()) | set(outgoing_map.keys())

    # ======================
    # 5. INSERT FRESH DATA
    # ======================
    for type_id in all_type_ids:
        summary = MonthlySummary(
            year=year,
            month=month,
            type_id=type_id,
            total_incoming=incoming_map.get(type_id, 0),
            total_outgoing=outgoing_map.get(type_id, 0)
        )
        db.add(summary)

    db.commit()

    return {"message": f"Aggregation success for {month}-{year}"}


# ======================
# CLEANUP FUNCTION
# ======================
def cleanup_old_logs(db: Session, days: int = 30):

    limit_date = datetime.now() - timedelta(days=days)

    db.query(IncomingLog).filter(
        IncomingLog.created_at < limit_date
    ).delete()

    db.query(OutgoingLog).filter(
        OutgoingLog.created_at < limit_date
    ).delete()

    db.commit()

    return {"message": "Old logs cleaned"}