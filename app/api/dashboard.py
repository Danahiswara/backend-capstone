from fastapi import APIRouter, Depends, Query
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy import extract

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.detection import Detection
from app.models.item import Item
from app.models.incoming_log import IncomingLog
from app.models.outgoing_log import OutgoingLog
from app.models.type import Type
from app.models.monthly_summary import MonthlySummary
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/types")
def get_types(
    search: str = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    query = db.query(Type)

    if search:
        search_lower = search.lower()

        query = query.filter(
            func.lower(Type.name).like(f"%{search_lower}%")
        )

        query = query.order_by(
            case(
                (func.lower(Type.name) == search_lower, 0),          # exact
                (func.lower(Type.name).like(f"{search_lower}%"), 1), # prefix
                else_=2
            ),
            Type.name.asc()
        )
    else:
        query = query.order_by(Type.name.asc())

    results = query.limit(limit).all()

    return [
        {
            "type_id": t.type_id,
            "name": t.name,
            "stock": t.total_items
        }
        for t in results
    ]

@router.get("/stock")
def get_stock(db: Session = Depends(get_db)):
    types = db.query(Type).all()

    return [
        {
            "type_id": t.type_id,
            "name": t.name,
            "stock": t.total_items
        }
        for t in types
    ]

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    total_incoming = db.query(
        func.sum(MonthlySummary.total_incoming)
    ).scalar() or 0

    total_outgoing = db.query(
        func.sum(MonthlySummary.total_outgoing)
    ).scalar() or 0

    current_stock = db.query(
        func.sum(Type.total_items)
    ).scalar() or 0

    return {
        "total_incoming": int(total_incoming),
        "total_outgoing": int(total_outgoing),
        "current_stock": int(current_stock)
    }

# @router.get("/monthly/incoming")
# def get_monthly_incoming(
#     db: Session = Depends(get_db),
#     _ = Depends(get_current_user)
# ):

#     results = db.query(
#         extract("year", Activity.detected_at).label("year"),
#         extract("month", Activity.detected_at).label("month"),
#         Activity.type_id,
#         func.sum(Activity.detected_sum).label("total")
#     ).group_by(
#         "year", "month", Activity.type_id
#     ).all()

#     data = []

#     for year, month, type_id, total in results:
#         data.append({
#             "year": int(year),
#             "month": int(month),
#             "type_id": type_id,
#             "total_incoming": int(total)
#         })

#     return data

# @router.get("/monthly/outgoing")
# def get_monthly_outgoing(
#     db: Session = Depends(get_db),
#     _ = Depends(get_current_user)
# ):

#     results = db.query(
#         extract("year", OutgoingLog.created_at).label("year"),
#         extract("month", OutgoingLog.created_at).label("month"),
#         OutgoingLog.type_id,
#         func.sum(OutgoingLog.quantity).label("total")
#     ).group_by(
#         "year", "month", OutgoingLog.type_id
#     ).all()

#     data = []

#     for year, month, type_id, total in results:
#         data.append({
#             "year": int(year),
#             "month": int(month),
#             "type_id": type_id,
#             "total_outgoing": int(total)
#         })

#     return data

@router.get("/monthly")
def get_monthly_summary(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    results = db.query(
        MonthlySummary.year,
        MonthlySummary.month,
        func.sum(MonthlySummary.total_incoming),
        func.sum(MonthlySummary.total_outgoing)
    ).group_by(
        MonthlySummary.year,
        MonthlySummary.month
    ).order_by(
        MonthlySummary.year,
        MonthlySummary.month
    ).all()

    return [
        {
            "year": y,
            "month": m,
            "total_incoming": int(i or 0),
            "total_outgoing": int(o or 0)
        }
        for y, m, i, o in results
    ]

@router.get("/monthly-by-type")
def get_monthly_by_type(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    results = db.query(
        MonthlySummary.year,
        MonthlySummary.month,
        MonthlySummary.type_id,
        MonthlySummary.total_incoming,
        MonthlySummary.total_outgoing
    ).all()

    return [
        {
            "year": r.year,
            "month": r.month,
            "type_id": r.type_id,
            "incoming": r.total_incoming,
            "outgoing": r.total_outgoing
        }
        for r in results
    ]

@router.get("/history/incoming")
def history_incoming(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    offset = (page - 1) * limit

    query = db.query(IncomingLog, Type)\
        .join(Type, Type.type_id == IncomingLog.type_id)

    # filter tanggal
    if year and month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + (month // 12), (month % 12) + 1, 1)

        query = query.filter(
            IncomingLog.created_at >= start_date,
            IncomingLog.created_at < end_date
        )

    total = query.count()

    results = query.order_by(
        IncomingLog.created_at.desc()
    ).offset(offset).limit(limit).all()

    data = []

    for incoming, type_data in results:
        data.append({
            "incoming_id": incoming.incoming_id,
            "type": type_data.name,
            "quantity": incoming.quantity,
            "created_at": incoming.created_at
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": data
    }

@router.get("/history/outgoing")
def history_outgoing(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    offset = (page - 1) * limit

    query = db.query(OutgoingLog, Type, Detection)\
        .join(Type, Type.type_id == OutgoingLog.type_id)\
        .outerjoin(Detection, Detection.detection_id == OutgoingLog.detection_id)

    # filter tanggal
    if year and month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + (month // 12), (month % 12) + 1, 1)

        query = query.filter(
            OutgoingLog.created_at >= start_date,
            OutgoingLog.created_at < end_date
        )

    total = query.count()

    results = query.order_by(
        OutgoingLog.created_at.desc()
    ).offset(offset).limit(limit).all()

    data = []

    for outgoing, type_data, detection in results:
        data.append({
            "outgoing_id": outgoing.outgoing_id,
            "type": type_data.name,
            "quantity": outgoing.quantity,
            "method": outgoing.method,
            "image": (
                detection.mask_path if outgoing.method == "ai" and detection
                else "default_stock_image.png"),
            "created_at": outgoing.created_at
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": data
    }
