from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
import asyncio

from settings import BOT_TOKEN, DATABASE_NAME
from db.db_manage import DataBase

from handlers.market import market_router
from handlers.admin_panel import admin_panel_router
from handlers.user_profile import user_profile_router
from bot.states import MassMessage

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(MassMessage.message)
async def mass_message(message: types.Message, state: FSMContext):
    await state.update_data(message=message.text)
    db = DataBase(DATABASE_NAME)
    users_id = db.get_users()
    db.__del__()
    data = await state.get_data()
    if type(users_id) != str:
        for user in users_id:
            await bot.send_message(user[0], data["message"])
    else:
        await message.answer(users_id)
    await state.clear()



async def main():
    dp.include_routers(market_router, admin_panel_router, user_profile_router)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
