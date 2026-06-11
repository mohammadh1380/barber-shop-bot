from sqlalchemy.orm import Session
from app.models.working_hours import WorkingHours


def get_worker_working_hours(db: Session, worker_id: int, weekday: int):
    return db.query(WorkingHours).filter(
        WorkingHours.worker_id == worker_id,
        WorkingHours.weekday == weekday
    ).first()
