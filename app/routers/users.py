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

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), 
    db: Session = Depends(db.get_db)):
    get_user = db.query(models.User).filter(models.User.email == get_current_user.email)
    if get_user.first() is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Utilisateur non trouvé"
        )
    get_user.delete(synchronize_session=False)
    
    db.commit()

@router.put("/update", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserResponse)
async def update_user(
    updated_user: schemas.UserUpdate, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)):
    try:
        # verifier si l'utilisateur courant existe
        current_user_db_info = db.query(models.User).filter(or_(models.User.email == get_current_user.email, models.User.id == get_current_user.id))
        # si non, renvoyer vers la router d'ajoute de compte
        if not current_user_db_info.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        
        # Vérifier si l'e-mail mis à jour existe déjà dans la base de données
        if updated_user.email != current_user_db_info.first().email:
            existing_user = db.query(models.User).filter(models.User.email == updated_user.email).first()
            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet e-mail est déjà utilisé par un autre utilisateur")
        # mise à jour de la date de modification
        updated_user.date_modif = datetime.now()
        # mise à jour du mot de passe s'il a été changé
        updated_user.password = current_user_db_info.first().password if updated_user.password is None else utils.hash_password(updated_user.password)
        # mise à jour de l'email s'il a été changé
        updated_user.email = current_user_db_info.first().email if updated_user.email is None else updated_user.email
        # mise à jour du nom s'il a été changé
        updated_user.nom = current_user_db_info.first().nom if updated_user.nom is None else updated_user.nom
        # initalisation des valeurs mises à jour
        current_user_db_info.update(updated_user.model_dump(), synchronize_session=False)
    except Exception as e:
        # Gérer toutes les autres exceptions ici
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db.commit()
    return current_user_db_info.first()