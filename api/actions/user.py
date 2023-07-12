from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import ShowUser
from api.models import UserCreate
from db.dals import UserDAL
from db.models import PortalRole
from db.models import User
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
            roles=[PortalRole.ROLE_PORTAL_USER],
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
) -> Optional[User]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(user_id=user_id)
        if user is not None:
            return user


def check_user_permission(target_user: User, current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id != current_user.user_id:
        if not {  # maybe this shit is wrong
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        if (
            PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
        if (
            PortalRole.ROLE_PORTAL_ADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
    return True
