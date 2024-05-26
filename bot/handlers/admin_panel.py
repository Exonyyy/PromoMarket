from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.filters import IsAdmin
from bot.keyboards import one_button_inline_keyboard, admin_menu_keyboard, column_items_keyboard
from bot.states import AddProduct, MassMessage, AddProductCount, ChangeProductPrice
from db.db_manage import DataBase
from settings import DATABASE_NAME

admin_panel_router = Router()


@admin_panel_router.callback_query(F.data == "admin_panel")
async def admin_menu_callback(callback: types.CallbackQuery):
    await admin_panel(callback.message)


@admin_panel_router.message(IsAdmin(), lambda message: message.text.lower() in ['админ панель', 'админ меню'])
async def admin_panel(message: types.Message):
    await message.answer("Вы находитесь в панеле администратора, выберите действие",
                         reply_markup=admin_menu_keyboard())


@admin_panel_router.callback_query(F.data == "add_product")
async def create_new_product(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddProduct.name)
    await callback.message.answer("Введите название", reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    await callback.answer()


@admin_panel_router.message(AddProduct.name)
async def get_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await state.set_state(AddProduct.price)
    await message.answer("Введите цену", reply_markup=one_button_inline_keyboard("Отменить", "cancel"))


@admin_panel_router.message(AddProduct.price)
async def get_product_price(message: types.Message, state: FSMContext):
    is_real = message.text.replace(".", "").isnumeric() and len(message.text[message.text.find(".")+1:]) <= 2
    if message.text.isnumeric() or is_real:
        await state.update_data(price=float(message.text))
        await state.set_state(AddProduct.count)
        await message.answer("Введите количество товаров",
                             reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    else:
        await message.answer("Вы ввели некорректную цену",
                             reply_markup=one_button_inline_keyboard("Отменить", "cancel"))


@admin_panel_router.message(AddProduct.count, lambda message: message.text.isnumeric())
async def get_product_count(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        await state.update_data(count=int(message.text))
        await state.set_state(AddProduct.market)
        await message.answer("Введите магазин", reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    else:
        await message.answer("Вы ввели некорректное количество товаров",
                             reply_markup=one_button_inline_keyboard("Отменить", "cancel"))


@admin_panel_router.message(AddProduct.market)
async def get_product(message: types.Message, state: FSMContext):
    await state.update_data(market=message.text)
    data = await state.get_data()
    data["market"] = data["market"].replace("ё", "е").replace(" ", "_").lower()
    db = DataBase(DATABASE_NAME)
    answer = db.add_product(data)
    if answer == "Product added successfully":
        await message.answer("Товар успешно добавлен в базу данных",
                             reply_markup=one_button_inline_keyboard("Добавить ещё товар", "add_product"))
    else:
        await message.answer("Что то пошло не так, попробуйте ещё раз",
                             reply_markup=one_button_inline_keyboard("Попробовать ещё раз", "add_product"))
    await state.clear()
    db.__del__()


@admin_panel_router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено", reply_markup=admin_menu_keyboard())
    await callback.answer()


@admin_panel_router.callback_query(F.data == "mass_message")
async def mass_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(MassMessage.message)
    await callback.message.answer("Введите сообщение, которое будет отправлено всем пользователям",
                                  reply_markup=one_button_inline_keyboard("Отменить", "cancel"))


@admin_panel_router.callback_query(F.data == "add_product_count")
async def get_product_name_for_change(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddProductCount.product_name)
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    product_names = [product[0] for product in products]

    await callback.message.answer("Выберите товар", reply_markup=column_items_keyboard(
        len(product_names), product_names))


@admin_panel_router.message(AddProductCount.product_name)
async def get_product_count(message: types.Message, state: FSMContext):
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    product_names = [product[0].title() for product in products]
    if message.text.title() in product_names:
        await state.update_data(product_name=message.text.title())
        await state.set_state(AddProductCount.count)
        await message.answer("Введите количество товара", reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    else:
        await message.answer("Такого товара не существует")


@admin_panel_router.message(AddProductCount.count)
async def add_product_count(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        await state.update_data(count=int(message.text))
        data = await state.get_data()
        await state.clear()
        db = DataBase(DATABASE_NAME)
        answer = db.add_product_count(data["product_name"], data["count"])
        db.__del__()
        if answer == "Successfully added":
            await message.answer("Количество товаров успешно обновленно",
                                 reply_markup=one_button_inline_keyboard("Админ меню", "admin_panel"))
        else:
            await message.answer("Что-то пошло не так, попробуйте ещё раз",
                                 reply_markup=one_button_inline_keyboard("Админ меню", "admin_panel"))
    else:
        await message.answer("Вы ввели не число")


@admin_panel_router.callback_query(F.data == "set_price")
async def get_product_name_for_change_price(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChangeProductPrice.product_name)
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    product_names = [product[0] for product in products]
    await callback.message.answer("Выберите товар", reply_markup=column_items_keyboard(
        len(product_names), product_names))


@admin_panel_router.message(ChangeProductPrice.product_name)
async def get_product_price(message: types.Message, state: FSMContext):
    db = DataBase(DATABASE_NAME)
    products = db.get_products()
    db.__del__()
    product_names = [product[0].title() for product in products]
    if message.text.title() in product_names:
        await state.update_data(product_name=message.text.title())
        await state.set_state(ChangeProductPrice.price)
        await message.answer("Введите новую цену", reply_markup=one_button_inline_keyboard("Отменить", "cancel"))
    else:
        await message.answer("Такого товара не существует")


@admin_panel_router.message(ChangeProductPrice.price)
async def add_product_count(message: types.Message, state: FSMContext):
    is_real = message.text.replace(".", "").isnumeric() and len(message.text[message.text.find("."):]) <= 2
    if is_real:
        await state.update_data(price=int(message.text))
        data = await state.get_data()
        await state.clear()
        db = DataBase(DATABASE_NAME)
        answer = db.change_product_price(data["product_name"], data["price"])
        db.__del__()
        if answer == "Successfully updated":
            await message.answer("Цена на товар успешно обновленно",
                                 reply_markup=one_button_inline_keyboard("Админ меню", "admin_panel"))
        else:
            await message.answer("Что-то пошло не так, попробуйте ещё раз",
                                 reply_markup=one_button_inline_keyboard("Админ меню", "admin_panel"))
    else:
        await message.answer("Вы ввели не цену")
