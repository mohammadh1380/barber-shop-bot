from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.appointment import Appointment


def is_slot_available(db: Session, worker_id: int, start, end) -> bool:
    conflict = db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.start_at < end,
        Appointment.end_at > start,
        Appointment.status == "booked"
    ).first()

    return conflict is None


def create_booking(db: Session, user_id: int, service_id: int, worker_id: int, start, duration_minutes: int):
    end = start + timedelta(minutes=duration_minutes)

    if not is_slot_available(db, worker_id, start, end):
        return None

    booking = Appointment(
        user_id=user_id,
        service_id=service_id,
        worker_id=worker_id,
        start_at=start,
        end_at=end,
        status="booked"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking
