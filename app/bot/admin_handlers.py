from aiogram import Router, types
from datetime import time

from app.bot.admin_guard import admin_only
from app.core.database import SessionLocal

from app.models.service import Service
from app.models.worker import Worker
from app.models.working_hours import WorkingHours
from app.models.holiday import Holiday

router = Router()

@router.message(lambda m: m.text and m.text.startswith("/add_service"))
@admin_only
async def add_service(message: types.Message):
    try:
        _, title, duration = message.text.split(" ", 2)
    except:
        await message.answer("فرمت: /add_service haircut 30")
        return

    db = SessionLocal()

    try:
        service = Service(
            title=title,
            duration_minutes=int(duration)
        )

        db.add(service)
        db.commit()

        await message.answer("سرویس اضافه شد ✅")

    finally:
        db.close()

@router.message(lambda m: m.text and m.text.startswith("/add_worker"))
@admin_only
async def add_worker(message: types.Message):
    try:
        _, name = message.text.split(" ", 1)
    except:
        await message.answer("فرمت: /add_worker Ali")
        return

    db = SessionLocal()

    try:
        worker = Worker(name=name, is_active=True)
        db.add(worker)
        db.commit()

        await message.answer("آرایشگر اضافه شد ✅")

    finally:
        db.close()

@router.message(lambda m: m.text and m.text.startswith("/set_hours"))
@admin_only
async def set_hours(message: types.Message):
    try:
        _, worker_id, weekday, start, end = message.text.split()
    except:
        await message.answer("فرمت: /set_hours 1 0 09:00 18:00")
        return

    db = SessionLocal()

    try:
        start_t = time.fromisoformat(start)
        end_t = time.fromisoformat(end)

        wh = WorkingHours(
            worker_id=int(worker_id),
            weekday=int(weekday),
            start_time=start_t,
            end_time=end_t
        )

        db.add(wh)
        db.commit()

        await message.answer("ساعت کاری ثبت شد ✅")

    finally:
        db.close()

@router.message(lambda m: m.text and m.text.startswith("/add_holiday"))
@admin_only
async def add_holiday(message: types.Message):
    try:
        _, date = message.text.split()
    except:
        await message.answer("فرمت: /add_holiday 2026-06-12")
        return

    db = SessionLocal()

    try:
        holiday = Holiday(holiday_date=date)
        db.add(holiday)
        db.commit()

        await message.answer("تعطیلی ثبت شد ❌")

    finally:
        db.close()
