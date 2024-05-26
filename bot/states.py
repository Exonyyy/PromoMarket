from aiogram.fsm.state import State, StatesGroup


class AddProduct(StatesGroup):
    name = State()
    price = State()
    count = State()
    market = State()


class BuyProduct(StatesGroup):
    market = State()
    name = State()
    count = State()


class MassMessage(StatesGroup):
    message = State()


class AddProductCount(StatesGroup):
    product_name = State()
    count = State()


class ChangeProductPrice(StatesGroup):
    product_name = State()
    price = State()


class TopUpUserBalance(StatesGroup):
    price = State()