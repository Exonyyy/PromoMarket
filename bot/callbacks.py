from aiogram.filters.callback_data import CallbackData


class UserPage(CallbackData, prefix="pageswap"):
    event: str
    page: int


class DealUser(CallbackData, prefix="confirm_deal"):
    event: str
    user_id: int
