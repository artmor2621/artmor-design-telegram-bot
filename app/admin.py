import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from app.database.requests import get_users
from app.states import Newsletter
import app.admin_keyboards as kb

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация роутера для администраторских команд
admin = Router()

# Фильтр для проверки прав администратора
class Admin(BaseFilter):
    def __init__(self, admins: list[int] = None):
        self.admins = admins or [1011762375]  # Задайте ID администратора

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admins

@admin.message(Admin(), Command("apanel"))
async def apanel(message: Message):
    """Обработчик команды /apanel, который выводит доступные команды для администратора"""
    await message.answer(
        "Возможные команды:\n"
        "/newsletter - для рассылки сообщений всем пользователям"
    )

@admin.message(Admin(), Command('newsletter'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Отправьте сообщение, которое вы хотите разослать всем пользователям')

@admin.message(Admin(), Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    progress_message = await message.answer('Подождите... идёт рассылка.')

    users = await get_users()
    total_users = len(users)

    success_count = 0
    failure_count = 0

    for idx, user in enumerate(users, start=1):
        try:
            await message.send_copy(chat_id=user.tg_id)
            success_count += 1
            logger.info(f"Сообщение отправлено пользователю {user.tg_id}")
        except Exception as e:
            failure_count += 1
            logger.error(f"Ошибка при отправке сообщения пользователю {user.tg_id}: {e}")

        # Рассчитываем прогресс
        progress = int((idx / total_users) * 100)

        # Обновляем сообщение с прогрессом
        await progress_message.edit_text(
            f"Рассылка: {progress}% ({idx}/{total_users})\n"
            f"Успешно отправлено: {success_count}\n"
            f"Ошибки при отправке: {failure_count}"
        )

        # Добавим паузу, чтобы избежать спама
        await asyncio.sleep(0.3)

    # Финальное сообщение о завершении рассылки
    await progress_message.edit_text(
        f"Рассылка завершена.\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибки при отправке: {failure_count}."
    )

    await state.clear()
