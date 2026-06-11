from sqlalchemy import Column, Integer, Date, ForeignKey
from app.core.database import Base


class WorkerLeave(Base):
    __tablename__ = "worker_leaves"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), index=True)

    start_date = Column(Date)
    end_date = Column(Date)
