from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User


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