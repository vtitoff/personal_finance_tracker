from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from schemas.user import CreateUserSchema, GetUserSchema
from services.exceptions import ConflictError, ObjectNotFoundError
from services.user_service import UserService, get_user_service
from utils.auth import (check_admin_access, check_user_access, decode_token,
                        oauth2_scheme)

router = APIRouter()


@router.get("/{user_id}", response_model=GetUserSchema)
async def get_user_by_id(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
) -> GetUserSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        user = await user_service.get_user_by_id(user_id)
        return GetUserSchema.model_validate(user)
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.get("/logins/{user_login}", response_model=GetUserSchema)
async def get_user_by_login(
    user_login: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_admin_access(payload)

        user = await user_service.get_user_by_login(user_login)
        return user
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.patch("/{user_id}", response_model=GetUserSchema)
async def update_user(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user: CreateUserSchema,
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        updated_user = await user_service.update_user(user_id, user)
        return updated_user
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.delete(
    "/{user_id}",
    response_model=dict,
)
async def delete_user(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        await user_service.delete_user(user_id=user_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
