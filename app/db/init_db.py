from app.db.base import Base
from app.db.session import engine

# Import semua model supaya ter-register
from app.models.user import User
from app.models.item import Item
from app.models.detection import Detection
from app.models.incoming_log import IncomingLog
from app.models.type import Type
from app.models.outgoing_log import OutgoingLog
from app.models.monthly_summary import MonthlySummary

def init_db():
    Base.metadata.create_all(bind=engine)
