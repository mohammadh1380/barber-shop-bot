from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime, timedelta, time

from app.bot.admin_guard import ADMIN_IDS
from app.core.database import SessionLocal
from app.models.service import Service
from app.models.worker import Worker
from app.services.booking_service import create_booking
from app.bot.state import BookingState, USER_STATE
from app.core.database import SessionLocal
from app.services.availability_service import generate_slots
from app.services.service_service import get_service

router = Router()


def build_main_menu(user_id: int):
    buttons = [
        [
            types.InlineKeyboardButton(text="✂️ خدمات", callback_data="menu_services"),
            types.InlineKeyboardButton(text="👨‍🔧 آرایشگرها", callback_data="menu_workers"),
        ],
        [
            types.InlineKeyboardButton(text="📅 رزرو نوبت", callback_data="menu_booking"),
            types.InlineKeyboardButton(text="ℹ️ راهنما", callback_data="menu_help"),
        ],
    ]

    if user_id in ADMIN_IDS:
        buttons.append([
            types.InlineKeyboardButton(text="🛠️ پنل مدیریت", callback_data="menu_admin"),
        ])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    text = (
        "سلام 👋\n"
        "به ربات رزرو نوبت آرایشگاه خوش آمدید.\n\n"
        "از منوی زیر برای مشاهده خدمات، آرایشگرها و راهنمای رزرو استفاده کنید."
    )

    await message.answer(text, reply_markup=build_main_menu(user_id))


@router.callback_query(lambda c: c.data == "menu_services")
async def menu_services(callback: types.CallbackQuery):
    db = SessionLocal()

    try:
        items = db.query(Service).order_by(Service.id).all()
        if not items:
            await callback.message.answer("در حال حاضر سرویس ثبت نشده است ❌")
            await callback.answer()
            return

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=f"{item.title} ({item.duration_minutes} دقیقه)", callback_data=f"choose_service_{item.id}")]
            for item in items
        ])
        keyboard.inline_keyboard.append([
            types.InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu_back")
        ])

        await callback.message.answer("💈 برای رزرو، یکی از خدمات زیر را انتخاب کنید:", reply_markup=keyboard)
    finally:
        db.close()

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("choose_service_"))
async def choose_service(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    service_id = int(callback.data.replace("choose_service_", ""))

    db = SessionLocal()

    try:
        service = get_service(db, service_id)
        if not service:
            await callback.message.answer("این سرویس موجود نیست ❌")
            await callback.answer()
            return

        USER_STATE[user_id] = BookingState(service_id=service_id)

        workers = db.query(Worker).filter(Worker.is_active.is_(True)).order_by(Worker.id).all()
        if not workers:
            await callback.message.answer("در حال حاضر آرایشگری فعال نیست ❌")
            await callback.answer()
            return

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=worker.name, callback_data=f"choose_worker_{worker.id}")]
            for worker in workers
        ])

        await callback.message.answer(
            f"سرویس انتخاب شد: {service.title}\n\n" "حالا آرایشگر مورد نظر را انتخاب کنید:",
            reply_markup=keyboard,
        )
    finally:
        db.close()

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("choose_worker_"))
async def choose_worker(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    worker_id = int(callback.data.replace("choose_worker_", ""))

    state = USER_STATE.get(user_id)
    if not state:
        await callback.message.answer("لطفاً ابتدا یک سرویس انتخاب کنید")
        await callback.answer()
        return

    state.worker_id = worker_id

    today = datetime.now().date()
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=f"{(today + timedelta(days=i)).strftime('%Y-%m-%d')}", callback_data=f"date_{(today + timedelta(days=i)).strftime('%Y-%m-%d')}")]
        for i in range(7)
    ])

    await callback.message.answer("📅 تاریخ مورد نظر را انتخاب کنید:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_workers")
async def menu_workers(callback: types.CallbackQuery):
    db = SessionLocal()

    try:
        items = db.query(Worker).filter(Worker.is_active.is_(True)).order_by(Worker.id).all()
        if not items:
            await callback.message.answer("در حال حاضر آرایشگری فعال نیست ❌")
        else:
            text = "👨‍🔧 آرایشگرهای فعال:\n\n"
            for item in items:
                text += f"• {item.name}\n"
            await callback.message.answer(text)
    finally:
        db.close()

    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_booking")
async def menu_booking(callback: types.CallbackQuery):
    text = (
        "📅 برای رزرو نوبت:\n"
        "1) ابتدا از منوی مدیریت سرویس و آرایشگرها، خدمات و آرایشگرها را اضافه کنید\n"
        "2) سپس از دکمه‌های رزرو داخل چت استفاده کنید\n"
        "3) در صورت نیاز، از دکمه «پنل مدیریت» کمک بگیرید"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_back")
async def menu_back(callback: types.CallbackQuery):
    await callback.message.answer(
        "✨ منوی اصلی\n\nانتخاب کنید:",
        reply_markup=build_main_menu(callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_help")
async def menu_help(callback: types.CallbackQuery):
    text = (
        "ℹ️ راهنما\n\n"
        "/start - نمایش منوی اصلی\n"
        "/admin - ورود به پنل مدیریت (برای ادمین)"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu_admin")
async def menu_admin(callback: types.CallbackQuery):
    await callback.message.answer("🛠️ پنل مدیریت در دسترس است. از دستور /admin استفاده کنید.")
    await callback.answer()

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
