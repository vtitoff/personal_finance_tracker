from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import AuthOutputSchema, LoginInputSchema, RefreshInputSchema
from schemas.user import CreateUserSchema
from services.auth_service import AuthService, get_auth_service
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.user_service import UserService, get_user_service
from utils.auth import decode_token

router = APIRouter()


@router.post("/signup", response_model=AuthOutputSchema)
async def signup(
    user: CreateUserSchema,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthOutputSchema:
    try:
        user = await user_service.create_user(user)
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already exists",
        )

    user_id = str(user.id)

    user_roles = [role.title for role in await user_service.get_user_roles(user_id)]

    access_token = await auth_service.generate_access_token(user_id, user_roles)
    refresh_token = await auth_service.generate_refresh_token(user_id)

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=AuthOutputSchema,
)
async def refresh(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:

    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    if not await auth_service.is_refresh_token_valid(request_data.refresh_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    access_token_data = decode_token(request_data.access_token)
    if access_token_data:
        await auth_service.invalidate_access_token(request_data.access_token)

    user_id = refresh_token_data["user_id"]

    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

    refresh_token, access_token = await auth_service.update_refresh_token(
        user_id,
        request_data.refresh_token,
        user_roles,
    )

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/login",
    response_model=AuthOutputSchema,
)
async def login(
    login_data: LoginInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:
    try:
        user = await user_service.get_user_by_login(login_data.login)

        if not user.check_password(login_data.password):
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail="invalid password")

        user_id = str(user.id)

        # await user_service.save_login_history(user_id) TODO

        user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

        access_token = await auth_service.generate_access_token(user_id, user_roles)
        refresh_token = await auth_service.generate_refresh_token(user_id)

        return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e)


@router.post("/logout", response_model=dict)
async def logout(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    await auth_service.invalidate_refresh_token(request_data.refresh_token)

    if decode_token(request_data.access_token):
        await auth_service.invalidate_access_token(request_data.access_token)

    return {"detail": "logout success"}


@router.post("/logout/all", response_model=dict)
async def logout_all(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    await auth_service.invalidate_user_refresh_tokens(
        refresh_token_data["user_id"], request_data.refresh_token
    )
    return {"detail": "logout from all other devices success"}


@router.post(
    "/token",
    response_model=AuthOutputSchema,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:
    try:
        user = await user_service.get_user_by_login(form_data.username)

        if not user.check_password(form_data.password):
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail="invalid password")

        user_id = str(user.id)

        # await user_service.save_login_history(user_id) TODO

        user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

        access_token = await auth_service.generate_access_token(user_id, user_roles)
        refresh_token = await auth_service.generate_refresh_token(user_id)

        return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e)
