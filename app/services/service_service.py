from sqlalchemy.orm import Session
from app.models.service import Service


def get_service(db: Session, service_id: int) -> Service:
    return db.query(Service).filter(Service.id == service_id).first()
