from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.payment_method import (CreatePaymentMethodSchema,
                                    GetPaymentMethodSchema)
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.payment_method_service import (PaymentMethod,
                                             PaymentMethodService,
                                             get_payment_method_service)

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
