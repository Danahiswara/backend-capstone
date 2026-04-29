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
    now = datetime.now()

    # range bulan sekarang (INDEX FRIENDLY)
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1)

    # ======================
    # 1. HISTORICAL (AGGREGATED)
    # ======================
    hist_in, hist_out = db.query(
        func.coalesce(func.sum(MonthlySummary.total_incoming), 0),
        func.coalesce(func.sum(MonthlySummary.total_outgoing), 0)
    ).first()

    # ======================
    # 2. REALTIME (BULAN SEKARANG)
    # ======================

    # incoming
    real_in = db.query(
        func.coalesce(func.sum(IncomingLog.quantity), 0)
    ).filter(
        IncomingLog.created_at >= start,
        IncomingLog.created_at < end
    ).scalar()

    # outgoing
    real_out = db.query(
        func.coalesce(func.sum(OutgoingLog.quantity), 0)
    ).filter(
        OutgoingLog.created_at >= start,
        OutgoingLog.created_at < end
    ).scalar()

    # ======================
    # 3. CURRENT STOCK
    # ======================
    current_stock = db.query(
        func.coalesce(func.sum(Type.total_items), 0)
    ).scalar()

    # ======================
    # 4. RESULT
    # ======================
    return {
        "total_incoming": int(hist_in + real_in),
        "total_outgoing": int(hist_out + real_out),
        "current_stock": int(current_stock)
    }

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

@router.get("/monthly-hybrid")
def get_monthly_hybrid(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1)

    # ======================
    # 1. HISTORICAL
    # ======================
    historical = db.query(
        MonthlySummary.year,
        MonthlySummary.month,
        Type.name,
        MonthlySummary.total_incoming,
        MonthlySummary.total_outgoing
    ).join(Type).filter(
        (MonthlySummary.year < now.year) |
        ((MonthlySummary.year == now.year) & (MonthlySummary.month < now.month))
    ).all()

    # ======================
    # 2. REALTIME INCOMING
    # ======================
    incoming = db.query(
        extract("year", IncomingLog.created_at).label("year"),
        extract("month", IncomingLog.created_at).label("month"),
        Type.name,
        func.sum(IncomingLog.quantity).label("incoming")
    )\
    .join(Type, Type.type_id == IncomingLog.type_id)\
    .filter(
        IncomingLog.created_at >= start,
        IncomingLog.created_at < end
    )\
    .group_by(
        extract("year", IncomingLog.created_at),
        extract("month", IncomingLog.created_at),
        Type.name
    ).all()

    # ======================
    # 3. REALTIME OUTGOING
    # ======================
    outgoing = db.query(
        extract("year", OutgoingLog.created_at).label("year"),
        extract("month", OutgoingLog.created_at).label("month"),
        Type.name,
        func.sum(OutgoingLog.quantity).label("outgoing")
    )\
    .join(Type, Type.type_id == OutgoingLog.type_id)\
    .filter(
        OutgoingLog.created_at >= start,
        OutgoingLog.created_at < end
    )\
    .group_by(
        extract("year", OutgoingLog.created_at),
        extract("month", OutgoingLog.created_at),
        Type.name
    ).all()

    # ======================
    # 4. MERGE (ANTI DUPLIKASI)
    # ======================
    data_map = {}

    # historical
    for h in historical:
        key = (h.year, h.month, h.name)
        data_map[key] = {
            "year": h.year,
            "month": h.month,
            "type": h.name,
            "incoming": int(h.total_incoming or 0),
            "outgoing": int(h.total_outgoing or 0),
            "source": "aggregated"
        }

    # incoming
    for i in incoming:
        key = (int(i.year), int(i.month), i.name)
        if key not in data_map:
            data_map[key] = {
                "year": int(i.year),
                "month": int(i.month),
                "type": i.name,
                "incoming": 0,
                "outgoing": 0,
                "source": "realtime"
            }
        data_map[key]["incoming"] += int(i.incoming or 0)

    # outgoing
    for o in outgoing:
        key = (int(o.year), int(o.month), o.name)
        if key not in data_map:
            data_map[key] = {
                "year": int(o.year),
                "month": int(o.month),
                "type": o.name,
                "incoming": 0,
                "outgoing": 0,
                "source": "realtime"
            }
        data_map[key]["outgoing"] += int(o.outgoing or 0)

    return list(data_map.values())

@router.get("/monthly-by-type")
def get_monthly_by_type(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    results = db.query(
        MonthlySummary.year,
        MonthlySummary.month,
        Type.name,
        MonthlySummary.total_incoming,
        MonthlySummary.total_outgoing
    ).join(Type, Type.type_id == MonthlySummary.type_id)\
     .order_by(
        MonthlySummary.year,
        MonthlySummary.month
     ).all()

    return [
        {
            "year": r.year,
            "month": r.month,
            "type": r.name,
            "incoming": int(r.total_incoming),
            "outgoing": int(r.total_outgoing)
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
                else None),
            "created_at": outgoing.created_at
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": data
    }
