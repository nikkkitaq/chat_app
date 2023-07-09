from logging import getLogger
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdatedUserRequest
from api.models import UpdatedUserResponse
from api.models import UserCreate
from db.dals import UserDAL
from db.session import get_db
from hashing import Hasher

logger = getLogger(__name__)

user_router = APIRouter()


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


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: UserCreate, session: AsyncSession = Depends(get_db)
) -> ShowUser:
    try:
        return await _create_new_user(body, session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> ShowUser:
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
    user_id: UUID, body: UpdatedUserRequest, session: AsyncSession = Depends(get_db)
) -> UpdatedUserResponse:
    updated_user_params = body.model_dump(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user = await _get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    try:
        updated_user_id = await _update_user(
            user_id=user_id, updated_user_params=updated_user_params, session=session
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)
