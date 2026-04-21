from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.incoming_log import IncomingLog
from app.models.outgoing_log import OutgoingLog
from app.models.monthly_summary import MonthlySummary


def aggregate_monthly(db: Session, year: int, month: int):

    # ambil incoming
    incoming_data = db.query(
        IncomingLog.type_id,
        func.sum(IncomingLog.quantity).label("total")
    ).filter(
        extract("year", IncomingLog.created_at) == year,
        extract("month", IncomingLog.created_at) == month
    ).group_by(IncomingLog.type_id).all()

    # ambil outgoing
    outgoing_data = db.query(
        OutgoingLog.type_id,
        func.sum(OutgoingLog.quantity).label("total")
    ).filter(
        extract("year", OutgoingLog.created_at) == year,
        extract("month", OutgoingLog.created_at) == month
    ).group_by(OutgoingLog.type_id).all()

    # convert ke dict
    incoming_map = {i.type_id: i.total for i in incoming_data}
    outgoing_map = {o.type_id: o.total for o in outgoing_data}

    all_type_ids = set(incoming_map.keys()) | set(outgoing_map.keys())

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