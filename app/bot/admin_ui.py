from datetime import time
from aiogram import Router, types

BACK_BUTTON_TEXT = "🔙 بازگشت"
from app.bot.admin_guard import admin_only
from app.bot.state import ADMIN_STATE
from app.core.database import SessionLocal
from app.models.worker import Worker
from app.models.service import Service
from app.models.working_hours import WorkingHours

router = Router()

@router.message(lambda m: m.text == "/admin")
@admin_only
async def admin_panel(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ سرویس‌ها", callback_data="admin_services")],
        [types.InlineKeyboardButton(text="👤 آرایشگرها", callback_data="admin_workers")],
        [types.InlineKeyboardButton(text="⏰ ساعات کاری", callback_data="admin_hours")],
        [types.InlineKeyboardButton(text="❌ تعطیلات", callback_data="admin_holidays")],
        [types.InlineKeyboardButton(text="📅 نوبت‌ها", callback_data="admin_appointments")],
    ])

    await message.answer("پنل مدیریت:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "admin_services")
@admin_only
async def services_menu(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ افزودن سرویس", callback_data="add_service")],
        [types.InlineKeyboardButton(text="📋 لیست سرویس‌ها", callback_data="list_services")],
        [types.InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_back")],
    ])

    await callback.message.edit_text("مدیریت سرویس‌ها:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "list_services")
@admin_only
async def list_services(callback: types.CallbackQuery):
    db = SessionLocal()

    try:
        items = db.query(Service).order_by(Service.id).all()

        if not items:
            await callback.message.answer("سرویسی وجود ندارد ❌")
            await callback.answer()
            return

        text = "لیست سرویس‌ها:\n\n"
        for item in items:
            text += f"• {item.id} - {item.title} ({item.duration_minutes} دقیقه)\n"

        await callback.message.answer(text)
    finally:
        db.close()

    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_workers")
@admin_only
async def workers_menu(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ افزودن آرایشگر", callback_data="add_worker")],
        [types.InlineKeyboardButton(text="📋 لیست آرایشگرها", callback_data="list_workers")],
        [types.InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_back")],
    ])

    await callback.message.edit_text("مدیریت آرایشگرها:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "add_service")
@admin_only
async def ask_service_title(callback: types.CallbackQuery):
    ADMIN_STATE[callback.from_user.id] = {"step": "service_title"}

    await callback.message.answer("نام سرویس را وارد کنید:")
    await callback.answer()

@router.message()
@admin_only
async def admin_text_router(message: types.Message):
    user_id = message.from_user.id
    state = ADMIN_STATE.get(user_id)

    if not state:
        return

    db = SessionLocal()

    try:
        step = state.get("step")

        # ----------------------
        # SERVICE FLOW
        # ----------------------
        if step == "service_title":
            state["title"] = message.text
            state["step"] = "service_duration"
            await message.answer("مدت زمان (دقیقه):")
            return

        if step == "service_duration":
            try:
                duration = int(message.text)
            except ValueError:
                await message.answer("عدد معتبر وارد کنید ❌")
                return

            db.add(Service(title=state["title"], duration_minutes=duration))
            db.commit()

            ADMIN_STATE.pop(user_id, None)
            await message.answer("سرویس ثبت شد ✅")
            return

        # ----------------------
        # WORKER FLOW
        # ----------------------
        if step == "worker_name":
            db.add(Worker(name=message.text, is_active=True))
            db.commit()

            ADMIN_STATE.pop(user_id, None)
            await message.answer("آرایشگر اضافه شد ✅")
            return

        # ----------------------
        # WORKING HOURS FLOW
        # ----------------------
        if step == "wh_worker":
            state["worker_id"] = int(message.text)
            state["step"] = "wh_weekday"
            await message.answer("روز هفته (0-6):")
            return

        if step == "wh_weekday":
            state["weekday"] = int(message.text)
            state["step"] = "wh_start"
            await message.answer("ساعت شروع:")
            return

        if step == "wh_start":
            state["start"] = message.text
            state["step"] = "wh_end"
            await message.answer("ساعت پایان:")
            return

        if step == "wh_end":
            from datetime import time

            wh = WorkingHours(
                worker_id=state["worker_id"],
                weekday=state["weekday"],
                start_time=time.fromisoformat(state["start"]),
                end_time=time.fromisoformat(message.text),
            )

            db.add(wh)
            db.commit()

            ADMIN_STATE.pop(user_id, None)
            await message.answer("ساعت کاری ثبت شد ✅")
            return

    finally:
        db.close()

@router.callback_query(lambda c: c.data == "add_worker")
@admin_only
async def add_worker_start(callback: types.CallbackQuery):
    ADMIN_STATE[callback.from_user.id] = {"step": "worker_name"}

    await callback.message.answer("نام آرایشگر را وارد کنید:")
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_back")
@admin_only
async def back(callback: types.CallbackQuery):
    await admin_panel(callback.message)
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_hours")
@admin_only
async def hours_menu(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ تنظیم ساعت کاری", callback_data="set_hours")],
        [types.InlineKeyboardButton(text="📋 مشاهده ساعت‌ها", callback_data="list_hours")],
        [types.InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_back")],
    ])

    await callback.message.edit_text("ساعات کاری:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "set_hours")
@admin_only
async def set_hours_start(callback: types.CallbackQuery):
    ADMIN_STATE[callback.from_user.id] = {"step": "wh_worker"}

    await callback.message.answer("ID آرایشگر را وارد کنید:")
    await callback.answer()

from app.models.appointment import Appointment

@router.callback_query(lambda c: c.data == "admin_appointments")
@admin_only
async def appointments_menu(callback: types.CallbackQuery):
    db = SessionLocal()

    try:
        items = db.query(Appointment).order_by(Appointment.start_at.desc()).limit(10).all()

        if not items:
            await callback.message.answer("نوبتی وجود ندارد ❌")
            await callback.answer()
            return

        text = "آخرین نوبت‌ها:\n\n"

        for a in items:
            text += f"""
👤 کاربر: {a.user_id}
💈 آرایشگر: {a.worker_id}
✂️ سرویس: {a.service_id}
🕒 شروع: {a.start_at}
🕓 پایان: {a.end_at}
-------------------
"""

        await callback.message.answer(text)

    finally:
        db.close()

    await callback.answer()