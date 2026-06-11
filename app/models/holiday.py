from sqlalchemy import Column, Integer, Date, String
from app.core.database import Base


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True)
    holiday_date = Column(Date, index=True)
    title = Column(String, nullable=True)
    