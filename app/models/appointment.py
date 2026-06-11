from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    worker_id = Column(Integer, ForeignKey("workers.id"))

    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)

    status = Column(String, default="booked")
