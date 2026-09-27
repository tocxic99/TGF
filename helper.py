from database import db
from config import Config


async def can_forward(user_id: int, count: int = 1):
    return await db.can_forward(user_id, count)


async def consume_forward(user_id: int, count: int = 1):
    return await db.consume_forward(user_id, count)