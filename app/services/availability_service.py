from datetime import datetime, timedelta, time
from typing import List

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.holiday import Holiday
from app.models.worker_leave import WorkerLeave
from app.services.working_hours_service import get_worker_working_hours

def is_holiday(db: Session, date: datetime) -> bool:
    return db.query(Holiday).filter(Holiday.holiday_date == date.date()).first() is not None

def is_worker_on_leave(db: Session, worker_id: int, date: datetime) -> bool:
    return db.query(WorkerLeave).filter(
        WorkerLeave.worker_id == worker_id,
        WorkerLeave.start_date <= date.date(),
        WorkerLeave.end_date >= date.date()
    ).first() is not None

def get_worker_appointments(db: Session, worker_id: int, date: datetime):
    start_day = datetime.combine(date.date(), time.min)
    end_day = datetime.combine(date.date(), time.max)

    return db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.start_at >= start_day,
        Appointment.start_at <= end_day,
        Appointment.status == "booked"
    ).all()

def is_slot_free(appointments, start: datetime, end: datetime) -> bool:
    for a in appointments:
        if a.start_at < end and a.end_at > start:
            return False
    return True

def generate_slots(db: Session, worker_id: int, date: datetime, duration_minutes: int):

    weekday = date.weekday()

    wh = get_worker_working_hours(db, worker_id, weekday)
    if not wh:
        return []

    # holidays
    holiday = db.query(Holiday).filter(Holiday.holiday_date == date.date()).first()
    if holiday:
        return []

    # leave
    leave = db.query(WorkerLeave).filter(
        WorkerLeave.worker_id == worker_id,
        WorkerLeave.start_date <= date.date(),
        WorkerLeave.end_date >= date.date()
    ).first()

    if leave:
        return []

    appointments = db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.start_at >= datetime.combine(date.date(), wh.start_time),
        Appointment.start_at <= datetime.combine(date.date(), wh.end_time),
        Appointment.status == "booked"
    ).all()

    slots = []

    current = datetime.combine(date.date(), wh.start_time)
    end = datetime.combine(date.date(), wh.end_time)

    delta = timedelta(minutes=duration_minutes)

    while current + delta <= end:

        slot_end = current + delta

        conflict = False
        for a in appointments:
            if a.start_at < slot_end and a.end_at > current:
                conflict = True
                break

        if not conflict:
            slots.append(current.strftime("%H:%M"))

        current += timedelta(minutes=15)

    return slots

