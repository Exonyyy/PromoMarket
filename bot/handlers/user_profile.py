from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
import emoji

from bot.keyboards import profile_menu_keyboard, one_button_inline_keyboard
from bot.states import TopUpUserBalance
from db.db_manage import DataBase
from settings import DATABASE_NAME

user_profile_router = Router()


@user_profile_router.callback_query(F.data == "user_profile")
async def user_profile(callback: types.CallbackQuery):
    db = DataBase(DATABASE_NAME)
    balance = db.get_user_balance(callback.from_user.id)
    db.__del__()
    text = f"Привет, {callback.message.from_user.first_name}!{emoji.emojize("\U0001F44B")}\nТвой баланс: {balance} руб"
    await callback.message.answer(text, reply_markup=profile_menu_keyboard())
    await callback.answer()


@user_profile_router.callback_query(F.data == "top_up_balance")
async def get_user_price(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TopUpUserBalance.price)
    await callback.message.answer("Введите сумму, На которую вы хотите пополнить баланс",
                                  reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    await callback.answer()


@user_profile_router.message(TopUpUserBalance.price)
async def top_up_user_balance(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        await state.update_data(price=int(message.text))
        data = await state.get_data()
        await state.clear()
        db = DataBase(DATABASE_NAME)
        answer = db.top_up_user_balance(message.from_user.id, data["price"])
        if answer == "Balance updated":
            await message.answer("Баланс пополнен",
                                 reply_markup=one_button_inline_keyboard("Профиль", "user_profile"))
        else:
            await message.answer("Произошла ошибка, попробуйте ещё раз",
                                 reply_markup=one_button_inline_keyboard("Профиль", "user_profile"))
    else:
        await message.answer("Вы ввели не число")
