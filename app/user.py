from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
import logging

from app.states import DesignRequestStates
from app.utils.validators import is_valid_email
from app.database.requests import set_user, save_request, get_user_orders
import app.user_keyboards as kb
from app.database.models import async_session, User


logger = logging.getLogger(__name__)

user = Router()


# Стартовое сообщение
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    photo_path = 'resource/Images/hello-image.png'
    caption = ("*artmor design* — место, где сложные задачи превращаются в простые решения, а уникальные идеи становятся реальностью\\.\n\n"
               "Мы помогаем брендам выделяться, создавая сильные и запоминающиеся проекты\\. Наш подход — внимание к деталям, нестандартное мышление и глубокое понимание каждого клиента\\. Мы создаём дизайн, который не только привлекает внимание, но и делает ваш бренд уверенным и узнаваемым\\.\n\n"
               ">Доверьте нам свою историю — мы расскажем её так, как никто другой\\.")  # Исправлено: "другая" -> "другой"
    try:
        photo = FSInputFile(photo_path)
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=caption,
            parse_mode="MarkdownV2",
            reply_markup=kb.get_main_keyboard()
        )
    except FileNotFoundError:
        logger.error("Ошибка: Приветственное изображение не найдено.")
        await message.answer("Приветственное изображение не найдено.", reply_markup=kb.get_main_keyboard())


# Обработка отзывов
@user.message(F.text == "Отзывы")
async def message_review(message: Message, state: FSMContext):
    photo_path = 'resource/Images/review.png'
    try:
        photo = FSInputFile(photo_path)
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            reply_markup=kb.review_keyboard()
        )
    except FileNotFoundError:
        logger.error("Ошибка: Изображение для отзывов не найдено.")
        await message.answer("Изображение для отзывов не найдено.", reply_markup=kb.review_keyboard())
    await state.clear()


# Обработка FAQ
@user.message(F.text == "FAQ")
async def faq(message: Message, state: FSMContext):
    faq_text = (
    "*1\\. Как заказать дизайн?*\n\n"
    ">Для того чтобы заказать дизайн, вам нужно выбрать нужную услугу, предоставить информацию о проекте, а затем предоставить свои контактные данные, чтобы мы могли с вами связаться и обсудить детали\\.\n\n"
    "*2\\. Как долго будет длиться выполнение заказа?*\n\n"
    ">Сроки выполнения зависят от сложности проекта\\. Обычно стандартный проект занимает от нескольких дней до нескольких недель\\. Мы сообщим точные сроки после получения всех необходимых данных от вас\\.\n\n"
    "*3\\. Можно ли внести изменения в дизайн после его утверждения?*\n\n"
    ">Мы предоставляем возможность внести изменения в дизайн в рамках оговоренной стоимости\\. Однако крупные изменения или переработки, которые выходят за рамки первоначального задания, могут потребовать дополнительной оплаты\\.\n\n"
    "*4\\. Какой тип файлов вы предоставляете по завершению работы?*\n\n"
    ">По завершению проекта мы предоставляем все исходные файлы в формате, удобном для дальнейшего использования, включая векторные изображения \\(например, \\.ai, \\.eps\\), растровые файлы \\(\\.jpg, \\.png\\) и другие форматы по запросу\\.\n\n"
    "*5\\. Какие гарантии я получаю, заказав дизайн?*\n\n"
    ">Мы гарантируем, что дизайн будет выполнен в соответствии с вашим техническим заданием и пожеланиями\\. Также, если по каким\\-то причинам вам не понравится результат, мы сделаем все необходимые правки до тех пор, пока вы не будете удовлетворены конечным результатом\\.\n\n"
    "*6\\. Как происходит оплата за услуги?*\n\n"
    ">Мы работаем по системе предоплаты\\. После подтверждения всех деталей, мы выставляем счет и начинаем работу\\. Оплата производится через банковский перевод\\.\n\n"
    "*7\\. Есть ли возможность получить консультацию по дизайну?*\n\n"
    ">Да, мы предоставляем консультации по вопросам дизайна, включая рекомендации по улучшению вашего фирменного стиля, веб\\-дизайна и других аспектов визуального оформления\\. Для получения консультации, вы можете связаться с нами по кнопке в самом низу этого сообщения\\.\n\n"
    "*8\\. Можно ли заказать срочный дизайн?*\n\n"
    ">Да, мы можем взять заказ в срочном порядке\\. Однако в этом случае стоимость услуги может быть увеличена в зависимости от сложности и срочности выполнения работы\\.\n\n"
    "*9\\. Что делать, если я потерял файл дизайна?*\n\n"
    ">Если вы потеряли файл, связанный с вашим проектом, свяжитесь с нами, и мы постараемся предоставить вам копию\\. Однако, если проект был завершен давно, мы не всегда можем гарантировать наличие файлов\\."
    )
    await message.answer(faq_text, parse_mode="MarkdownV2", reply_markup=kb.support())


# Обработка портфолио
@user.message(F.text == "Портфолио")
async def message_portfolio(message: Message, state: FSMContext):
    photo_path = 'resource/Images/portfolio.png'
    try:
        photo = FSInputFile(photo_path)
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            reply_markup=kb.portfolio_keyboard()
        )
    except FileNotFoundError:
        logger.error("Ошибка: Изображение для портфолио не найдено.")
        await message.answer("Изображение для портфолио не найдено.", reply_markup=kb.portfolio_keyboard())
    await state.clear()


# Начало заказа дизайна
@user.message(F.text == "Заказать дизайн")
async def start_design_request(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, выберите, что вам необходимо:", reply_markup=kb.get_design_request_inline_keyboard())
    await state.set_state(DesignRequestStates.waiting_what_to_design)


@user.callback_query(F.data.in_([  # Фильтрация по типам дизайна
    "design_firm_style", "design_website", "design_social_media", "design_motion", "design_other"
]))
async def process_design_type(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(what_to_design=callback_query.data)
    await callback_query.message.answer("Пожалуйста, укажите ваш email.")
    await state.set_state(DesignRequestStates.waiting_email)


# Обработка email
@user.message(DesignRequestStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("Некорректный email. Попробуйте снова.")
        return
    await state.update_data(email=message.text)
    await message.answer("Отправьте ваш номер телефона для связи.", reply_markup=kb.get_phone())
    await state.set_state(DesignRequestStates.waiting_contact)


# Обработка номера телефона
@user.message(DesignRequestStates.waiting_contact)
async def process_contact(message: Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Ошибка: Пожалуйста, отправьте корректный номер телефона.")
        return

    await state.update_data(contact=message.contact.phone_number)
    await message.answer("Несколько слов о проекте и приблизительный бюджет.")
    await state.set_state(DesignRequestStates.waiting_project_info)


# Обработка описания задачи
@user.message(DesignRequestStates.waiting_project_info)
async def process_project_info(message: Message, state: FSMContext):
    data = await state.get_data()
    data["project_info"] = message.text
    await save_request(
        user_id=message.from_user.id,
        project_info=data.get("project_info"),
        email=data.get("email"),
        contact=data.get("contact"),
        status=data.get("status")
    )
    await message.answer(
        "Заявка успешно отправлена! В ближайшее время с вами свяжется менеджер.",
        reply_markup=kb.get_main_keyboard()
    )
    await state.clear()    


@user.message(F.text == "Статус заказа")
async def show_order_status(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id  # Получаем ID пользователя

        # Получаем все заказы пользователя
        orders = await get_user_orders(user_id)  # Передаем только user_id, а не session

        if not orders:
            await message.answer("У вас нет активных заказов.")
        else:
            # Формируем текст с состоянием заказов
            order_statuses = "\n".join(
                [f"*Заявка №{order.id}:* {order.status.value}" for order in orders]
            )
            await message.answer(f"Ваши заявки:\n\n{order_statuses}", parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при запросе статуса заказов: {e}")
        await message.answer("Произошла ошибка при получении информации о заказах. Попробуйте позже.")
