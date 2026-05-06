from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.type import Type


def create_type(
    db: Session,
    name: str,
    komposisi: str = None,
    farmasi: str = None,
    distributor: str = None,
    total_items: int = 0
):
    # optional: cek duplikat nama
    existing = db.query(Type).filter(Type.name == name).first()
    if existing:
        raise HTTPException(400, "Obat already exists")

    new_type = Type(
        name=name,
        komposisi=komposisi,
        farmasi=farmasi,
        distributor=distributor,
        total_items=total_items,
        is_active="true"
    )

    db.add(new_type)
    db.commit()
    db.refresh(new_type)

    return new_type

def update_type(
    db: Session,
    type_id: int,
    name: str = None,
    komposisi: str = None,
    farmasi: str = None,
    distributor: str = None,
    total_items: int = None
):
    type_data = db.query(Type).filter(Type.type_id == type_id).first()

    if not type_data:
        raise HTTPException(404, "Obat not found")

    if name is not None:
        type_data.name = name
    if komposisi is not None:
        type_data.komposisi = komposisi
    if farmasi is not None:
        type_data.farmasi = farmasi
    if distributor is not None:
        type_data.distributor = distributor
    if total_items is not None:
        type_data.total_items = total_items

    db.commit()
    db.refresh(type_data)

    return type_data

def get_pending_users(db: Session):
    return db.query(User).filter(User.is_approved == False).all()


def reject_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_approved:
        raise HTTPException(400, "User already approved, cannot reject")

    db.delete(user)
    db.commit()

    return {"message": "User registration rejected"}


def approve_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_approved:
        raise HTTPException(400, "User already approved")

    user.is_approved = True
    db.commit()

    return {"message": "User approved successfully"}


def get_approved_petugas(db: Session):
    return db.query(User).filter(
        User.role == "petugas",
        User.is_approved == True
    ).all()


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.role == "admin":
        raise HTTPException(400, "Cannot delete admin")
    
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}