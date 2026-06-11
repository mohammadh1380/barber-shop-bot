from sqlalchemy import Column, Integer, Time, ForeignKey
from app.core.database import Base


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True)

    worker_id = Column(Integer, ForeignKey("workers.id"), index=True)

    weekday = Column(Integer)  # 0=Monday ... 6=Sunday

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    