from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db
from app.crud.user_crud import delete_user, get_user_by_email, get_user_by_id, get_users, update_user_by_id
from app.schemas.user_schema import UserOut

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de usuarios a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima de usuarios a retornar")
):
    try:
        result = get_users(db, skip=skip, limit=limit)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email_route(email: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    try:
        user = update_user_by_id(db, user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.delete("/{user_id}", response_model=UserOut)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = delete_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")