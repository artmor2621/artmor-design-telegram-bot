from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Заказать дизайн")],
            [KeyboardButton(text="Портфолио"), KeyboardButton(text="Отзывы")],
            [KeyboardButton(text="Статус заказа"), KeyboardButton(text="FAQ")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие ниже"
    )


def get_design_request_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Логотип", callback_data="design_firm_style")],
            [InlineKeyboardButton(text="Айдентика", callback_data="design_website")],
            [InlineKeyboardButton(text="Дизайн сайта", callback_data="design_social_media")],
            [InlineKeyboardButton(text="Моушен-дизайн", callback_data="design_motion")],
            [InlineKeyboardButton(text="Другое", callback_data="design_other")]
        ]
    )


def support():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/artmordesign")],
        ]
    )


def portfolio_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Портфолио', url='https://t.me/+cq__jqskKZpiOTI6')]
        ]
    )


def review_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отзывы', url='https://t.me/+_shoXvbV6Xg1YWYy')]
        ]
    )


def get_phone():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить контакт", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="Нажмите, чтобы отправить номер телефона ↓"
    )