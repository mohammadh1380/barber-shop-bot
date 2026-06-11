from aiogram import Router, types
from datetime import datetime, time

from app.services.booking_service import create_booking
from app.bot.state import USER_STATE
from app.core.database import SessionLocal
from app.services.availability_service import generate_slots
from app.services.service_service import get_service

router = Router()

@router.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("ربات فعال است ✅")

@router.callback_query(lambda c: c.data.startswith("date_"))
async def select_date(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    state = USER_STATE[user_id]

    state.date = callback.data.replace("date_", "")

    db = SessionLocal()

    try:
        service = get_service(db, state.service_id)
        if not service:
            await callback.message.answer("خدمت پیدا نشد ❌")
            await callback.answer()
            return

        duration = service.duration_minutes

        from app.services.availability_service import generate_slots

        slots = generate_slots(
            db=db,
            worker_id=state.worker_id,
            date=datetime.strptime(state.date, "%Y-%m-%d"),
            duration_minutes=duration
        )

        if not slots:
            await callback.message.answer("هیچ تایم خالی وجود ندارد ❌")
            await callback.answer()
            return

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=s, callback_data=f"time_{s}")]
                for s in slots
            ]
        )

        await callback.message.answer("ساعت مورد نظر را انتخاب کنید:", reply_markup=keyboard)
        await callback.answer()

    finally:
        db.close()

# -------------------------
# TIME SELECTION (FINAL STEP)
# -------------------------
@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    time_str = callback.data.replace("time_", "")

    state = USER_STATE.get(user_id)

    if not state:
        await callback.message.answer("سشن منقضی شده است")
        await callback.answer()
        return

    db = SessionLocal()

    try:
        service = get_service(db, state.service_id)
        if not service:
            await callback.message.answer("خدمت معتبر نیست ❌")
            return

        start = datetime.strptime(
            f"{state.date} {time_str}",
            "%Y-%m-%d %H:%M"
        )

        booking = create_booking(
            db=db,
            user_id=user_id,
            service_id=state.service_id,
            worker_id=state.worker_id,
            start=start,
            duration_minutes=service.duration_minutes
        )

        if not booking:
            await callback.message.answer("این تایم قبلاً رزرو شده است ❌")
            return

        await callback.message.answer(
            "رزرو شما با موفقیت ثبت شد ✅\n"
            f"خدمت: {service.title}\n"
            f"تاریخ: {state.date}\n"
            f"ساعت: {time_str}"
        )

        await callback.answer()

    finally:
        db.close()
