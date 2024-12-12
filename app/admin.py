from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, BaseFilter
from app.database.requests import get_user_orders, change_order_status, delete_order
import app.admin_keyboards as kb

admin = Router()

# Фильтр для проверки прав администратора
class Admin(BaseFilter):
    def __init__(self):
        self.admins = [1011762375]  # ID администратора

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins