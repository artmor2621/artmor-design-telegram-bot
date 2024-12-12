from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import async_session
from app.database.models import User
from sqlalchemy.orm import selectinload


async def set_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.tg_id == user_id))
            user = result.scalars().first()
            
            if not user:
                user = User(tg_id=user_id)
                session.add(user)

async def get_users(limit: int = 100, offset: int = 0):
    async with async_session() as session:
        result = await session.execute(select(User).offset(offset).limit(limit))
        users = result.scalars().all() 
    return users
