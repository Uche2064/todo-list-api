from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from .. import db, models, schemas, utils, oauth2

router = APIRouter(
    prefix="/users",
    tags=["User"]
)
@router.get("/", status_code=status.HTTP_202_ACCEPTED, response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(db.get_db)):
    users = db.query(models.User).all()
    return users


@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.CreateUser, db: Session = Depends(db.get_db)):
    # verifier si l'utilisateur existe deja
    get_user = db.query(models.User).filter(models.User.email == user.email).first()
    # si oui, envoyer un message d'erreur
    if get_user != None:
        raise HTTPException(status_code=status.HTTP_306_RESERVED, detail=f"Ce utilisateur existe déjà")
    # si non, enregistrer l'utilisateur
    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user    

@router.get("/{email}", status_code=status.HTTP_302_FOUND, response_model=schemas.UserResponse)
async def get_user(email: EmailStr, db: Session = Depends(db.get_db)):
    get_user = db.query(models.User).filter(models.User.email == email).first()
    
    if get_user is None: 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Utilisateur non trouvé"
        )
    return get_user

@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(email: EmailStr, db: Session = Depends(db.get_db)):
    get_user = db.query(models.User).filter(models.User.email == email)
    if get_user.first() is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Utilisateur non trouvé"
        )
    get_user.delete(synchronize_session=False)
    
    db.commit()

@router.put("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserResponse)
async def update_user(
    updated_user: schemas.UserUpdate, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)):
    
    # verifier si l'utilisateur existe
    get_user = db.query(models.User).filter(models.User.email == get_current_user.email)
    # si non, renvoyer vers la router d'ajoute de compte
    if not get_user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    # si oui, faire la modification
    updated_user.date_modif = datetime.now()
    updated_user.password = utils.hash_password(updated_user.password)
    get_user.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    return get_user.first()