from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.wallet import (CreateWalletSchema, GetWalletSchema,
                            UpdateWalletSchema)
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.wallet_service import WalletService, get_wallet_service
from sqlalchemy.exc import DBAPIError
from utils.auth import check_user_access, decode_token, oauth2_scheme

router = APIRouter()


@router.post("/", response_model=GetWalletSchema)
async def create_wallet(
    wallet: CreateWalletSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    wallet_service: WalletService = Depends(get_wallet_service),
) -> GetWalletSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(wallet.user_id))

        wallet = await wallet_service.create_wallet(wallet)
        return wallet
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet {wallet.id if hasattr(wallet, "id") else wallet.name} already exists",
        )


@router.patch("/{wallet_id}", response_model=GetWalletSchema)
async def update_wallet(
    wallet_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    wallet: UpdateWalletSchema,
    wallet_service: WalletService = Depends(get_wallet_service),
) -> GetWalletSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(wallet.user_id))

        updated_wallet = await wallet_service.update_wallet(wallet_id, wallet)
        return updated_wallet
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )


@router.get("/{wallet_id}", response_model=GetWalletSchema)
async def get_wallet_by_id(
    wallet_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    wallet_service: WalletService = Depends(get_wallet_service),
) -> GetWalletSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        wallet = await wallet_service.get_wallet_by_id(wallet_id)
        return wallet
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet is not found!",
        )


@router.get("/users/{user_id}", response_model=Page[GetWalletSchema])
async def get_wallet_by_user_id(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    wallet_service: WalletService = Depends(get_wallet_service),
) -> Page[GetWalletSchema]:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        wallets = await wallet_service.get_wallets_by_user_id(user_id)
        return paginate(wallets)
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallets is not found!",
        )


@router.delete(
    "/{wallet_id}",
    response_model=dict,
)
async def delete_wallet(
    wallet_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    wallet_service: WalletService = Depends(get_wallet_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        await wallet_service.delete_wallet(wallet_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
