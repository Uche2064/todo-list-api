from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import EmailStr
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .. import db, models, schemas, utils, oauth2

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

# Créer un nouvel utilisateur
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.CreateUser, db: Session = Depends(db.get_db)):
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet utilisateur existe déjà")
        
        # Hasher le mot de passe avant de l'enregistrer
        user.password = utils.hash_password(user.password)
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Obtenir un utilisateur par son adresse e-mail
@router.get("/{email}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
async def get_user(email: EmailStr, db: Session = Depends(db.get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Supprimer l'utilisateur actuel
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), 
    db: Session = Depends(db.get_db)
):
    try:
        user = db.query(models.User).filter(models.User.email == get_current_user.email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        db.delete(user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Mettre à jour les informations de l'utilisateur actuel
@router.put("/update", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
async def update_user(
    updated_user: schemas.UserUpdate, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)
):
    try:
        user = db.query(models.User).filter(or_(models.User.email == get_current_user.email, models.User.id == get_current_user.id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        
        if updated_user.email != user.email:
            existing_user = db.query(models.User).filter(models.User.email == updated_user.email).first()
            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet e-mail est déjà utilisé par un autre utilisateur")
        
        updated_user_data = updated_user.model_dump(exclude_unset=True)
        if updated_user_data.get('password'):
            updated_user_data['password'] = utils.hash_password(updated_user_data['password'])
        
        for key, value in updated_user_data.items():
            setattr(user, key, value)
        
        db.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
