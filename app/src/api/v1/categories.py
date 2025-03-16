from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.payment_category import (CreatePaymentCategorySchema,
                                      GetPaymentCategorySchema)
from services.category_service import CategoryService, get_category_service
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)

router = APIRouter()


@router.get("/categories", response_model=Page[GetPaymentCategorySchema])
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> Page[GetPaymentCategorySchema]:
    categories = await category_service.get_all_categories()
    return paginate(categories)


@router.post("/categories", response_model=dict)
async def create_categories(
    category: CreatePaymentCategorySchema,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        category = await category_service.create_category(category)
        return category
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {category.name} already exists",
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
