from aiogram import types

ADMIN_IDS = {1611491612}


def admin_only(handler):
    async def wrapper(event: types.TelegramObject, *args):
        user_id = None

        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id

        if user_id not in ADMIN_IDS:
            if isinstance(event, types.CallbackQuery):
                await event.answer("اجازه دسترسی ندارید ❌", show_alert=True)
            else:
                await event.answer("اجازه دسترسی ندارید ❌")
            return

        return await handler(event)

    return wrapper
