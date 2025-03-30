from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.payment_method import (CreatePaymentMethodSchema,
                                    GetPaymentMethodSchema,
                                    UpdatePaymentMethodSchema)
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.payment_method_service import (PaymentMethodService,
                                             get_payment_method_service)
from sqlalchemy.exc import DBAPIError
from utils.auth import check_user_access, decode_token, oauth2_scheme

router = APIRouter()


@router.post("/", response_model=GetPaymentMethodSchema)
async def create_payment_method(
    payment_method: CreatePaymentMethodSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payment_method.user_id))

        payment_method = await payment_method_service.create_payment_method(
            payment_method
        )
        return payment_method
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment method {payment_method.id if hasattr(payment_method, "id") else payment_method.name} already exists",
        )


@router.patch("/{payment_method_id}", response_model=GetPaymentMethodSchema)
async def update_payment_method(
    payment_method_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    payment_method: UpdatePaymentMethodSchema,
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payment_method.user_id))

        updated_payment_method = await payment_method_service.update_payment_method(
            payment_method_id, payment_method
        )
        return updated_payment_method
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.get("/{payment_method_id}", response_model=GetPaymentMethodSchema)
async def get_payment_method_by_id(
    payment_method_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> GetPaymentMethodSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        payment_method = await payment_method_service.get_payment_method_by_id(
            payment_method_id
        )
        return payment_method
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment method is not found!",
        )


@router.get("/users/{user_id}", response_model=Page[GetPaymentMethodSchema])
async def get_payment_method_by_user_id(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
) -> Page[GetPaymentMethodSchema]:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

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
    access_token: Annotated[str, Depends(oauth2_scheme)],
    payment_method_service: PaymentMethodService = Depends(get_payment_method_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        await payment_method_service.delete_payment_method(payment_method_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
