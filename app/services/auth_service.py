from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

def register_user(db: Session, name: str, email: str, password: str):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role="petugas",
        is_approved="False"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Register Success, Waiting For Admin Approval"
    }


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user.role=="petugas"and not user.is_approved:
        raise HTTPException(status_code=403, detail="Account not approved by admin")

    token = create_access_token(data={"sub": str(user.user_id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
