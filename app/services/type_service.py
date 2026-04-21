from sqlalchemy.orm import Session
from app.models.type import Type

def get_type_by_name(db: Session, name: str):
    return db.query(Type).filter(Type.name == name).first()