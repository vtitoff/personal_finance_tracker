from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from schemas.role import CreateRoleSchema, GetRoleSchema
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.role_service import RoleService, get_role_service
from sqlalchemy.exc import DBAPIError
from utils.auth import (check_admin_access, check_user_access, decode_token,
                        oauth2_scheme)

router = APIRouter()


@router.post("/", response_model=GetRoleSchema)
async def create_role(
    role: CreateRoleSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
) -> GetRoleSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_admin_access(payload)

        role = await role_service.create_role(role)
        return role
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role {role.id if hasattr(role, "id") else role.title} already exists",
        )


@router.get("/", response_model=Page[GetRoleSchema])
async def get_all_roles(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
) -> Page[GetRoleSchema]:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_admin_access(payload)

        roles = await role_service.get_all_roles()
        return paginate(roles)
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roles is not found!",
        )


@router.get("/{role_id}", response_model=GetRoleSchema)
async def get_role_by_id(
    role_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
) -> GetRoleSchema:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        role = await role_service.get_role_by_id(role_id)
        return role
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role is not found!",
        )


@router.get("/users/{user_id}", response_model=Page[GetRoleSchema])
async def get_roles_by_user_id(
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
) -> Page[GetRoleSchema]:
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, user_id)

        roles = await role_service.get_user_roles(user_id)
        return paginate(roles)
    except (ObjectNotFoundError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roles is not found!",
        )


@router.delete(
    "/{role_id}",
    response_model=dict,
)
async def delete_role(
    role_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_user_access(payload, str(payload["user_id"]))

        await role_service.delete_role(role_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/{role_id}/assign",
    response_model=dict,
)
async def assign_role(
    role_id: str,
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_admin_access(payload)

        await role_service.assign_role_to_user(user_id, role_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/{role_id}/remove",
    response_model=dict,
)
async def remove_role(
    role_id: str,
    user_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    role_service: RoleService = Depends(get_role_service),
):
    try:
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token"
            )

        check_admin_access(payload)

        await role_service.remove_role_from_user(user_id, role_id)
        return {"detail": "success"}
    except ObjectNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
