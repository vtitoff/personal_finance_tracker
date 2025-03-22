from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from schemas.user import CreateUserSchema, GetUserSchema
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.user_service import UserService, get_user_service

router = APIRouter()


@router.get("/users/{user_id}", response_model=GetUserSchema)
async def get_user_by_id(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
) -> GetUserSchema:
    try:
        user = await user_service.get_user_by_id(user_id)
        return GetUserSchema.model_validate(user)
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.get("/logins/{user_login}", response_model=GetUserSchema)
async def get_user_by_login(
    user_login: str,
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        user = await user_service.get_user_by_login(user_login)
        return user
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.patch("/users/{user_id}", response_model=GetUserSchema)
async def update_user(
    user_id: str,
    user: CreateUserSchema,
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        updated_user = await user_service.update_user(user_id, user)
        return updated_user
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.delete(
    "/users/{user_id}",
    response_model=dict,
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.delete_user(user_id=user_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
