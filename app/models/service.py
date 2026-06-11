from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    