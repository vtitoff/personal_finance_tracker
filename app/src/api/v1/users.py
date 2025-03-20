from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
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
        return user
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post("/users/create", response_model=GetUserSchema)
async def create_user(
    user: CreateUserSchema,
    user_service: UserService = Depends(get_user_service),
) -> GetUserSchema:
    try:
        user = await user_service.create_user(user)
        return user
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already exists",
        )


# @router.patch("/users/{user_id}", response_model=GetUserSchema)
# async def update_category(
#     user_id: str,
#     user: CreateUserSchema,
#     user_service: UserService = Depends(get_user_service),
# ) -> GetUserSchema:
#     try:
#         updated_user = await user_service.update_user(user_id, user)
#         return updated_user
#     except ConflictError as error:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=error,
#         )
