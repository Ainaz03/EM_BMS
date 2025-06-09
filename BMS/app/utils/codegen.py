import string
import secrets
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.team import Team

async def generate_unique_invite_code(
    db: AsyncSession,
    length: int = 8,
    alphabet: str = string.ascii_uppercase + string.digits,
) -> str:
    """
    Генерирует случайный код заданной длины и проверяет его уникальность в БД.
    Цикл повторяется, пока не найдётся свободный код.
    """
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        q = await db.execute(select(Team).where(Team.invite_code == code))
        if not q.scalars().first():
            return code
