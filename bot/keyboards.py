from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton, InlineKeyboardButton, InlineKeyboardBuilder
import math

from bot.callbacks import UserPage, DealUser
from settings import MAX_COLUMN_LEN


def menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Товары", callback_data="product_list"),
                InlineKeyboardButton(text="Профиль", callback_data="user_profile"))
    builder.row(InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance"))
    return builder.as_markup()


def one_button_inline_keyboard(button_text, button_data):
    return InlineKeyboardBuilder().add(InlineKeyboardButton(text=button_text, callback_data=button_data)).as_markup()


def deal_button(button_text, event, user_id):
    return InlineKeyboardBuilder().add(
        InlineKeyboardButton(text=button_text, callback_data=DealUser(event=event, user_id=user_id).pack())).as_markup()


def pagination(pages: int, page: int = 1):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="<<", callback_data=UserPage(event="prev", page=page).pack()),
                InlineKeyboardButton(text=f"Страница: {page}/{pages}", callback_data="page"),
                InlineKeyboardButton(text=">>", callback_data=UserPage(event="next", page=page).pack()))
    builder.row(InlineKeyboardButton(text="Купить", callback_data="buy_product"))
    return builder.as_markup()


def column_items_keyboard(items_count: int, items_text: list):
    builder = ReplyKeyboardBuilder()
    columns = math.ceil(items_count / MAX_COLUMN_LEN)
    buttons = list()
    for button in range(items_count):
        buttons.append(KeyboardButton(text=items_text[button]))
    for row in range(0, items_count, columns):
        button_row = list()
        last_n = row+columns if row+columns <= items_count else items_count
        for column in range(row, last_n):
            button_row.append(buttons[column])
        builder.row(*button_row)
    return builder.as_markup(resize_keyboard=True)


def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить товар", callback_data="add_product"),
                InlineKeyboardButton(text="Рассылка", callback_data="mass_message"))
    builder.row(InlineKeyboardButton(text="Пополнить количество товаров", callback_data="add_product_count"),
                InlineKeyboardButton(text="Изменить цену на товар", callback_data="set_price"))
    return builder.as_markup()


def profile_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance"))
    builder.add(InlineKeyboardButton(text="Меню", callback_data="menu"))
    return builder.as_markup()
