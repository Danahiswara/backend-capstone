from fastapi import APIRouter, Depends, Query, HTTPException
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

    # 1. HISTORICAL (AGGREGATED)
    hist_in, hist_out = db.query(
        func.coalesce(func.sum(MonthlySummary.total_incoming), 0),
        func.coalesce(func.sum(MonthlySummary.total_outgoing), 0)
    ).first()

    # 2. REALTIME (BULAN SEKARANG)

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

    # 3. CURRENT STOCK
    current_stock = db.query(
        func.coalesce(func.sum(Type.total_items), 0)
    ).scalar()

    # 4. RESULT
    return {
        "total_incoming": int(hist_in + real_in),
        "total_outgoing": int(hist_out + real_out),
        "current_stock": int(current_stock)
    }

@router.get("/top-distributor")
def top_distributor(db: Session = Depends(get_db)):
    result = db.query(
        Type.distributor,
        func.count(Type.type_id).label("total")
    ).filter(
        Type.distributor.isnot(None)
    ).group_by(Type.distributor)\
     .order_by(func.count(Type.type_id).desc())\
     .all()

    return result

@router.get("/top-farmasi")
def top_farmasi(db: Session = Depends(get_db)):
    result = db.query(
        Type.farmasi,
        func.count(Type.type_id).label("total")
    ).filter(
        Type.farmasi.isnot(None)
    ).group_by(Type.farmasi)\
     .order_by(func.count(Type.type_id).desc())\
     .all()

    return result

@router.get("/top-outgoing-last-month")
def top_outgoing_last_month(db: Session = Depends(get_db)):
    now = datetime.now()

    if now.month == 1:
        year = now.year - 1
        month = 12
    else:
        year = now.year
        month = now.month - 1

    result = db.query(
        Type.name,
        func.sum(OutgoingLog.quantity).label("total_out")
    ).join(OutgoingLog)\
     .filter(
        extract("year", OutgoingLog.created_at) == year,
        extract("month", OutgoingLog.created_at) == month
    )\
     .group_by(Type.name)\
     .order_by(func.sum(OutgoingLog.quantity).desc())\
     .limit(5)\
     .all()

    return result

@router.get("/yearly-trend")
def yearly_trend(year: int, db: Session = Depends(get_db)):
    result = db.query(
        MonthlySummary.month,
        func.sum(MonthlySummary.total_incoming).label("incoming"),
        func.sum(MonthlySummary.total_outgoing).label("outgoing")
    ).filter(
        MonthlySummary.year == year
    ).group_by(MonthlySummary.month)\
     .order_by(MonthlySummary.month)\
     .all()

    return result

@router.get("/peak-month")
def peak_month(year: int, db: Session = Depends(get_db)):
    data = db.query(
        MonthlySummary.month,
        func.sum(MonthlySummary.total_incoming).label("incoming"),
        func.sum(MonthlySummary.total_outgoing).label("outgoing")
    ).filter(
        MonthlySummary.year == year
    ).group_by(MonthlySummary.month).all()

    max_in = max(data, key=lambda x: x.incoming or 0)
    max_out = max(data, key=lambda x: x.outgoing or 0)

    return {
        "highest_incoming": max_in,
        "highest_outgoing": max_out
    }

@router.get("/stock-difference")
def stock_difference(db: Session = Depends(get_db)):
    now = datetime.now()

    def get_total(year, month):
        return db.query(
            func.sum(MonthlySummary.total_incoming - MonthlySummary.total_outgoing)
        ).filter(
            MonthlySummary.year == year,
            MonthlySummary.month == month
        ).scalar() or 0

    # bulan ini
    current = get_total(now.year, now.month)

    # bulan lalu
    if now.month == 1:
        prev = get_total(now.year - 1, 12)
    else:
        prev = get_total(now.year, now.month - 1)

    diff = current - prev

    return {
        "current": current,
        "previous": prev,
        "difference": diff,
        "status": "naik" if diff > 0 else "turun" if diff < 0 else "stabil"
    }

@router.get("/type-detail/{type_id}")
def type_detail(type_id: int, db: Session = Depends(get_db)):
    data = db.query(Type).filter(Type.type_id == type_id).first()

    if not data:
        raise HTTPException(404, "Type not found")

    return {
        "name": data.name,
        "komposisi": data.komposisi,
        "farmasi": data.farmasi,
        "distributor": data.distributor
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

    # 1. HISTORICAL
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

    # 2. REALTIME INCOMING
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

    # 3. REALTIME OUTGOING
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

    # 4. MERGE (ANTI DUPLIKASI)
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
