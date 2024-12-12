import enum
from sqlalchemy import ForeignKey, String, BigInteger, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs

from config import DB_URL

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(DB_URL, echo=True)

# Настройка sessionmaker для асинхронных сессий
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для всех моделей с поддержкой асинхронных аттрибутов
Base = declarative_base()  # Здесь нет AsyncAttrs, так как это только для моделей

# Модель User
class User(Base):
    __tablename__ = 'users'  # Указание имени таблицы

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True, nullable=False)

    orders: Mapped[list['Order']] = relationship(back_populates="user", cascade="all, delete-orphan")

# Статусы заказа
class OrderStatus(enum.Enum):
    pending = "🔃 В ожидании"
    in_progress = "🔥 В работе"
    completed = "✅ Завершен"
    canceled = "❌ Отменен"

# Модель Order
class Order(Base):
    __tablename__ = 'orders'  # Указание имени таблицы

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)

    user: Mapped['User'] = relationship(back_populates="orders")

# Асинхронная функция для создания всех таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
