from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.payment_category import (CreatePaymentCategorySchema,
                                      GetPaymentCategorySchema)
from services.category_service import CategoryService, get_category_service
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from utils.auth import (check_admin_access, check_user_access, decode_token,
                        oauth2_scheme)

router = APIRouter()


@router.get("/", response_model=Page[GetPaymentCategorySchema])
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> Page[GetPaymentCategorySchema]:
    categories = await category_service.get_all_categories()
    return paginate(categories)


@router.get("/{category_id}", response_model=GetPaymentCategorySchema)
async def get_categories(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service),
) -> GetPaymentCategorySchema:
    try:
        category = await category_service.get_category_by_id(category_id)
        return category
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post("/", response_model=GetPaymentCategorySchema)
async def create_categories(
    category: CreatePaymentCategorySchema,
    category_service: CategoryService = Depends(get_category_service),
) -> GetPaymentCategorySchema:
    try:
        category = await category_service.create_category(category)
        return category
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {category.name} already exists",
        )


@router.patch("/", response_model=GetPaymentCategorySchema)
async def update_category(
    category_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    category: CreatePaymentCategorySchema,
    category_service: CategoryService = Depends(get_category_service),
) -> GetPaymentCategorySchema:
    try:

        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        user_id = payload["user_id"]
        # check_admin_access(payload, user_id)
        check_user_access(payload, user_id)

        updated_category = await category_service.update_category(category_id, category)
        return updated_category
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.delete(
    "/{category_id}",
    response_model=dict,
)
async def delete_category(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        await category_service.delete_category(category_id=category_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
