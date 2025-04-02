from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.outgoing_transaction import (CreateOutgoingTransactionSchema,
                                          GetOutgoingTransactionSchema,
                                          UpdateOutgoingTransactionSchema)
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.transaction_service import (OutgoingTransactionService,
                                          get_outgoing_transaction_service)
from sqlalchemy.exc import DBAPIError
from utils.auth import check_user_access, decode_token, oauth2_scheme

router = APIRouter()


@router.post("/", response_model=GetOutgoingTransactionSchema)
async def create_transaction(
    transaction: CreateOutgoingTransactionSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    transaction_service: OutgoingTransactionService = Depends(
        get_outgoing_transaction_service
    ),
) -> GetOutgoingTransactionSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(transaction.user_id))

        transaction = await transaction_service.create_transaction(transaction)
        return transaction
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction {transaction.id if hasattr(transaction, "id") else transaction.name} already exists",
        )


@router.patch("/{transaction_id}", response_model=GetOutgoingTransactionSchema)
async def update_transaction(
    transaction_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    transaction: UpdateOutgoingTransactionSchema,
    transaction_service: OutgoingTransactionService = Depends(
        get_outgoing_transaction_service
    ),
) -> GetOutgoingTransactionSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(transaction.user_id))

        updated_transaction = await transaction_service.update_transaction(
            transaction_id, transaction
        )
        return updated_transaction
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.get("/{transaction_id}", response_model=GetOutgoingTransactionSchema)
async def get_transaction_by_id(
    transaction_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    transaction_service: OutgoingTransactionService = Depends(
        get_outgoing_transaction_service
    ),
) -> GetOutgoingTransactionSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        transaction = await transaction_service.get_transaction_by_id(transaction_id)
        return transaction
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction is not found!",
        )


@router.get("/users/{user_id}", response_model=Page[GetOutgoingTransactionSchema])
async def get_transactions_by_user_id(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    transaction_service: OutgoingTransactionService = Depends(
        get_outgoing_transaction_service
    ),
) -> Page[GetOutgoingTransactionSchema]:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        transactions = await transaction_service.get_transactions_by_user_id(user_id)
        return paginate(transactions)
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transactions is not found!",
        )


@router.delete(
    "/{transaction_id}",
    response_model=dict,
)
async def delete_transaction(
    transaction_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    transaction_service: OutgoingTransactionService = Depends(
        get_outgoing_transaction_service
    ),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        await transaction_service.delete_transaction(transaction_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
