from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from .. import db, models, schemas

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
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user    

@router.put("/update/{email}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserResponse)
async def update_user(updated_user: schemas.UserUpdate, email: EmailStr, db: Session = Depends(db.get_db)):
    # verifier si l'utilisateur existe
    get_user = db.query(models.User).filter(models.User.email == email)
    # si non, renvoyer vers la router d'ajoute de compte
    if not get_user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    # si oui, faire la modification
    updated_user.date_modif = datetime.now()
    get_user.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    return get_user.first()