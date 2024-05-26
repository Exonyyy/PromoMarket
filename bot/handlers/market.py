from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
import emoji

from settings import DATABASE_NAME
from bot.keyboards import *
from db.db_manage import DataBase
from bot.utils import get_table, sort_data_by_market
from bot.callbacks import UserPage, DealUser
from bot.states import BuyProduct


market_router = Router()


@market_router.message(Command("start"))
async def start(message: types.Message):
    db = DataBase(DATABASE_NAME)
    user_data = {"name": message.from_user.username, "balance": 0.0, "id": message.from_user.id}
    db.add_user(user_data)
    db.__del__()
    text = f"{emoji.emojize("\U0000270B")}Привет! Добро пожаловать в маркет промокодов!" \
           f" Здесь вы можете купить промокод на интересующие вас товары,"
    await message.answer(text)
    await menu(message)


@market_router.callback_query(F.data == "menu")
async def go_to_menu(callback: types.CallbackQuery):
    await menu(callback.message)


@market_router.message(lambda message: message.text.lower() in ["меню", 'главная', 'главное', 'главное меню'])
async def menu(message: types.Message):
    await message.answer("Выберите действие ниже", reply_markup=menu_keyboard())


@market_router.callback_query(F.data == "product_list")
async def product_list(callback: types.CallbackQuery):
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    if type(products) != str:
        txt, last_page = get_table(products)
        await callback.message.answer(txt, reply_markup=pagination(last_page))
    else:
        await callback.message.answer(products)
    await callback.answer()


@market_router.callback_query(UserPage.filter(F.call == "prev"))
async def previous_page(callback: types.CallbackQuery, callback_data: UserPage):
    page = callback_data.page - 1 if callback_data.page > 1 else callback_data.page
    try:
        db = DataBase(DATABASE_NAME)
        products = db.get_products()
        db.__del__()
        if type(products) != str:
            txt, last_page = get_table(products)
            await callback.message.answer(txt, reply_markup=pagination(last_page, page))
        else:
            await callback.message.answer(products)
    except TelegramBadRequest:
        pass
    finally:
        await callback.answer()


@market_router.callback_query(UserPage.filter(F.call == "next"))
async def next_page(callback: types.CallbackQuery, callback_data: UserPage):
    page = callback_data.page + 1 if callback_data.page < callback_data.pages else callback_data.page
    try:
        db = DataBase(DATABASE_NAME)
        products = db.get_products()
        db.__del__()
        if type(products) != str:
            txt, last_page = get_table(products)
            await callback.message.answer(txt, reply_markup=pagination(last_page, page))
        else:
            await callback.message.answer("Произошла ошибка, попробуйте позже")
    except TelegramBadRequest:
        pass
    finally:
        await callback.answer()


@market_router.callback_query(F.data == "buy_product")
async def get_market(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BuyProduct.market)
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    if type(products) != str:
        markets = sort_data_by_market(products).keys()
        await callback.message.answer("Выберите магазин, из которого вы хотите купить товар",
                                      reply_markup=column_items_keyboard(len(markets), list(markets)))
    else:
        await callback.message.answer("Произошла ошибка, попробуйте позже")
    await callback.answer()


@market_router.message(BuyProduct.market)
async def get_product_name(message: types.Message, state: FSMContext):
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    markets_product = sort_data_by_market(products)
    if message.text.lower() in [market.lower() for market in list(markets_product.keys())]:
        await state.update_data(market=message.text.title())
        await state.set_state(BuyProduct.name)
        await message.answer("Выберите товар",
                             reply_markup=column_items_keyboard(len(markets_product[message.text.title()]),
                                            list(product[1] for product in markets_product[message.text.title()])))
    else:
        await message.answer("Магазинн не найден")


@market_router.message(BuyProduct.name)
async def get_product_count(message: types.Message, state: FSMContext):
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    markets_product = list(sort_data_by_market(products).values())
    if message.text.lower() in [product[1].lower() for product in markets_product[0]]:
        await state.update_data(name=message.text.title())
        await state.set_state(BuyProduct.count)
        for product in markets_product[0]:
            if product[1] == message.text.title():
                count = product[3]
                await message.answer(f"Введите количество товара (до {count})")
    else:
        await message.answer("Такого товара не существует")


@market_router.message(BuyProduct.count)
async def confirm_deal(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        await state.update_data(count=int(message.text))
        product_data = await state.get_data()
        await message.answer(f"Вы хотите купить из магазина {product_data["market"]} {product_data["name"]}"
                             f" {product_data["count"]} шт. верно?", reply_markup=deal_button(
            "Оплатить", "confirm_deal", message.from_user.id))
    else:
        await message.answer("Вы ввели не число")


@market_router.callback_query(DealUser.filter(F.event == "confirm_deal"))
async def buy_product(callback: types.CallbackQuery, state: FSMContext, callback_data: DealUser):
    product_data = await state.get_data()
    await state.clear()
    db = DataBase(DATABASE_NAME)
    answer = db.buy_product(product_data, callback_data.user_id)
    if answer == "Недостаточно средств на балансе":
        await callback.message.answer(answer,
                                      reply_markup=one_button_inline_keyboard("Пополнить баланс", "top_up_balance"))
    else:
        await callback.message.answer(answer)
    await callback.answer()
    db.__del__()
