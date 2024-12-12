import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.states import DesignRequestStates
from app.utils.validators import is_valid_email
import app.user_keyboards as kb
import app.admin_keyboards as akb
from app.database.requests import set_user

# Настройка логирования
logger = logging.getLogger(__name__)
user = Router()

# Словарь перевода типа дизайна
design_types = {
    "logotype": "Логотип",
    "identy": "Айдентика",
    "web_design": "Веб-дизайн",
    "design_motion": "Моушн-дизайн",
    "design_other": "Другое"
}

# Вспомогательная функция для отправки фото с подписью и клавиатурой
async def send_photo_with_keyboard(message: Message, photo_path: str, caption: str, keyboard):
    try:
        photo = FSInputFile(photo_path)
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=caption,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
    except FileNotFoundError:
        logger.error("Файл не найден: %s", photo_path)
        await message.answer("Приветственное изображение не найдено.", reply_markup=keyboard)


# Команда старта
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    photo_path = 'resource/Images/hello-image.png'
    caption = (
        "*artmor design* — место, где сложные задачи превращаются в простые решения, "
        "а уникальные идеи становятся реальностью\\.\n\n"
        "Мы помогаем брендам выделяться, создавая сильные и запоминающиеся проекты\\. "
        "Наш подход — внимание к деталям, нестандартное мышление и глубокое понимание каждого клиента\\. "
        "Мы создаём дизайн, который не только привлекает внимание, но и делает ваш бренд уверенным и узнаваемым\\.\n\n"
        ">Доверьте нам свою историю — мы расскажем её так, как никто другой\\."
    )
    
    await send_photo_with_keyboard(message, photo_path, caption, kb.get_main_keyboard())


# Начало запроса на дизайн
@user.message(F.text == "Заказать дизайн")
async def start_design_request(message: Message, state: FSMContext):
    await message.answer(
        "📝 Укажите название проекта:", 
    )
    await state.set_state(DesignRequestStates.waiting_project_name)


# Обработка названия проекта
@user.message(DesignRequestStates.waiting_project_name)
async def process_project_name(message: Message, state: FSMContext):
    project_name = message.text.strip()
    if not project_name:
        await message.answer("Пожалуйста, укажите название проекта.")
        return
    await state.update_data(project_name=project_name)
    await message.answer(
        "📲 Пожалуйста, выберите, что вам необходимо:", 
        reply_markup=kb.get_design_request_inline_keyboard()
    )
    await state.set_state(DesignRequestStates.waiting_what_to_design)


# Обработка выбора типа дизайна
@user.callback_query(F.data.in_([ 
    "logotype", "identy", "web_design", "design_motion", "design_other"
]))
async def process_design_type(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(what_to_design=callback_query.data)
    await callback_query.message.answer("✉️ Пожалуйста, укажите ваш email.")
    await state.set_state(DesignRequestStates.waiting_email)


# Обработка email
@user.message(DesignRequestStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("Некорректный email. Попробуйте снова.")
        return
    await state.update_data(email=message.text)
    await message.answer("📞 Отправьте ваш номер телефона для связи.", reply_markup=kb.get_phone())
    await state.set_state(DesignRequestStates.waiting_contact)


# Обработка контакта
@user.message(DesignRequestStates.waiting_contact)
async def process_contact(message: Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Ошибка: Пожалуйста, отправьте корректный номер телефона.")
        return
    await state.update_data(contact=message.contact.phone_number)
    await message.answer("✍️ Несколько слов о проекте и приблизительный бюджет.")
    await state.set_state(DesignRequestStates.waiting_project_info)


# Обработка информации о проекте
@user.message(DesignRequestStates.waiting_project_info)
async def process_project_info(message: Message, state: FSMContext):
    await state.update_data(project_info=message.text)
    await message.answer("📃 Загрузите документ или нажмите 'Пропустить'", reply_markup=kb.get_skip_button())
    await state.set_state(DesignRequestStates.waiting_for_file)


# Обработка файла
@user.message(DesignRequestStates.waiting_for_file, F.content_type == ContentType.DOCUMENT)
async def handle_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_name = message.document.file_name
    await state.update_data(file=file_id, file_name=file_name)
    await finalize_request(message, state)


# Пропуск загрузки файла
@user.message(DesignRequestStates.waiting_for_file, F.text == "Пропустить")
async def skip_file(message: Message, state: FSMContext):
    await finalize_request(message, state)


# Финализация запроса
async def finalize_request(message: Message, state: FSMContext):
    data = await state.get_data()

    # Преобразование типа дизайна с английского на русский
    what_to_design = design_types.get(data.get('what_to_design', ''), 'Не указано')

    confirmation_message = (
        f"*— Название проекта:* {data.get('project_name', 'Не указано')}\n" 
        f"*— Тип дизайна:* {what_to_design}\n"
        f"*— Email:* {data.get('email', 'Не указан')}\n"
        f"*— Номер телефона:* {data.get('contact', 'Не указан')}\n"
        f"*— Информация о проекте:* {data.get('project_info', 'Не указана')}\n"
        f"*— Файл:* {data.get('file_name', 'Не загружен')}\n\n"
        f"⚠️ Наш специалист свяжется с вами в ближайшее время для уточнения деталей."
    )

    # Отправка подтверждения пользователю
    await message.answer(confirmation_message, parse_mode="Markdown", reply_markup=kb.get_main_keyboard())

    group_chat_id = -1002459041373
    user_id = message.from_user.id
    file_id = data.get('file')
    file_name = data.get('file_name')

    # Отправка данных в админский чат
    if file_id:
        await message.bot.send_document(
            chat_id=group_chat_id,
            document=file_id,
            caption=( 
                f"*Название проекта:* {data.get('project_name', 'Не указано')}\n\n"
                f"*Тип дизайна:* {what_to_design}\n"
                f"*Email:* {data.get('email', 'Не указан')}\n"
                f"*Номер телефона:* {data.get('contact', 'Не указан')}\n"
                f"*Информация о проекте:* {data.get('project_info', 'Не указана')}\n"
            ),
            parse_mode="Markdown",
            reply_markup=akb.get_user_chat_keyboard(user_id=user_id)
        )
    else:
        await message.bot.send_message(
            chat_id=group_chat_id,
            text=( 
                f"*Название проекта:* {data.get('project_name', 'Не указано')}\n\n"
                f"*Тип дизайна:* {what_to_design}\n"
                f"*Email:* {data.get('email', 'Не указан')}\n"
                f"*Номер телефона:* {data.get('contact', 'Не указан')}\n"
                f"*Информация о проекте:* {data.get('project_info', 'Не указана')}\n"
            ),
            parse_mode="Markdown",
            reply_markup=akb.get_user_chat_keyboard(user_id=user_id)
        )

    # Очистка состояния
    await state.clear()


# Обработка кнопок "Отзывы", "FAQ", "Портфолио"
@user.message(F.text == "Отзывы")
async def message_review(message: Message, bot: Bot, state: FSMContext):
    await send_photo_with_keyboard(message, 'resource/Images/review.png', "", kb.review_keyboard())
    await state.clear()


@user.message(F.text == "FAQ")
async def faq(message: Message, bot: Bot, state: FSMContext):
    faq_text = (
        "*1\\. Как заказать дизайн?*\n\n"
        ">Для того чтобы заказать дизайн, вам нужно выбрать нужную услугу, предоставить информацию о проекте и свои контактные данные, чтобы мы могли с вами связаться и обсудить детали\\.\n\n"
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


@user.message(F.text == "Портфолио")
async def message_portfolio(message: Message, bot: Bot, state: FSMContext):
    await send_photo_with_keyboard(message, 'resource/Images/portfolio.png', "", kb.portfolio_keyboard())
    await state.clear()
