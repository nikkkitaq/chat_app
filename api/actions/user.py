from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import ShowUser
from api.models import UserCreate
from db.dals import UserDAL
from db.session import get_db
from hashing import Hasher


async def _create_new_user(
    body: UserCreate, session: AsyncSession = Depends(get_db)
) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> Optional[UUID]:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(user_id=user_id)
        return deleted_user_id


async def _update_user(
    user_id: UUID, updated_user_params: dict, session: AsyncSession = Depends(get_db)
) -> Optional[UUID]:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id


async def _get_user_by_id(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> Optional[ShowUser]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(user_id=user_id)
        if user is not None:
            return ShowUser(
                user_id=user_id,
                name=user.name,
                email=user.email,
                is_active=user.is_active,
            )