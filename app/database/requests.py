from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import async_session
from app.database.models import User, Order, OrderStatus
from sqlalchemy.orm import selectinload


async def set_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.tg_id == user_id))
            user = result.scalars().first()
            
            if not user:
                user = User(tg_id=user_id)
                session.add(user)

async def save_request(user_id: int, project_info: str, email: str, contact: str, status: OrderStatus):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.tg_id == user_id))
            user = result.scalars().first()

            if not user:
                raise ValueError("Пользователь не найден в базе данных")

            order = Order(
                user_id=user.id,
                phone_number=contact,
                email=email,
                description=project_info,
                status=status
            )
            session.add(order)
            await session.commit()

async def get_user_orders(tg_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        
        if not user:
            return None

        result = await session.execute(select(Order).where(Order.user_id == user.id))
        orders = result.scalars().all()
        
        return orders


async def change_order_status(order_id: int, new_status: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Order).filter(Order.id == order_id))
            order = result.scalars().first()
            if order:
                if new_status in OrderStatus.__members__:
                    order.status = OrderStatus[new_status]
                    await session.commit()
                    await send_status_change_notification(bot, order.user_id, order.id, order.status.value)
                else:
                    raise ValueError("Неверный статус заказа")
            else:
                raise ValueError(f"Заказ с ID {order_id} не найден")


async def delete_order(order_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Order).filter(Order.id == order_id))
            order = result.scalars().first()
            if order:
                await session.delete(order)
                await session.commit()


async def send_status_change_notification(user_id: int, order_id: int, new_status: str):
    await bot.send_message(user_id, f"Статус вашей заявки №{order_id} изменён на: {new_status}")
