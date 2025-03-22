from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth import AuthOutputSchema
from schemas.user import CreateUserSchema
from services.auth_service import AuthService, get_auth_service
from services.exceptions import ObjectAlreadyExistsException
from services.user_service import UserService, get_user_service

router = APIRouter()


@router.post("/auth/signup", response_model=AuthOutputSchema)
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
