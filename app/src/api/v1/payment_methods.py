from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.payment_method import (CreatePaymentMethodSchema,
                                    GetPaymentMethodSchema,
                                    UpdatePaymentMethodSchema)
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.payment_method_service import (PaymentMethodService,
                                             get_payment_method_service)
from sqlalchemy.exc import DBAPIError

router = APIRouter()


@router.post("/payment_methods", response_model=GetPaymentMethodSchema)
async def create_payment_method(
    payment_method: CreatePaymentMethodSchema,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        payment_method = await payment_method_service.create_payment_method(
            payment_method
        )
        return payment_method
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment method {payment_method.id if hasattr(payment_method, "id") else payment_method.name} already exists",
        )


@router.patch(
    "/payment_methods/{payment_method_id}", response_model=GetPaymentMethodSchema
)
async def update_category(
    payment_method_id: str,
    payment_method: UpdatePaymentMethodSchema,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        updated_payment_method = await payment_method_service.update_payment_method(
            payment_method_id, payment_method
        )
        return updated_payment_method
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.get(
    "/payment_methods/{payment_method_id}", response_model=GetPaymentMethodSchema
)
async def get_payment_method_by_id(
    payment_method_id: str,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        payment_method = await payment_method_service.get_payment_method_by_id(
            payment_method_id
        )
        return payment_method
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment method is not found!",
        )


@router.get(
    "/payment_methods/users/{user_id}", response_model=Page[GetPaymentMethodSchema]
)
async def get_payment_method_by_user_id(
    user_id: str,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> Page[GetPaymentMethodSchema]:
    try:
        payment_methods = await payment_method_service.get_payment_methods_by_user_id(
            user_id
        )
        return paginate(payment_methods)
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment methods is not found!",
        )


@router.delete(
    "/{payment_method_id}",
    response_model=dict,
)
async def delete_payment_method(
    payment_method_id: str,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
):
    try:
        await payment_method_service.delete_payment_method(payment_method_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
