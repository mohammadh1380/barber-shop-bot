from app.core.database import Base, engine
from app.models.user import User
from app.models.worker import Worker
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.holiday import Holiday
from app.models.worker_leave import WorkerLeave

Base.metadata.create_all(bind=engine)
