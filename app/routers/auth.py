from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import db, models, utils, oauth2
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

@router.post("/",status_code=status.HTTP_202_ACCEPTED)
async def login(user_form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    get_user = db.query(models.User).filter(models.User.email == user_form_data.username).first()
    if get_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Utilisateur non trouvé"
        )
    
    if not utils.verify_password(user_form_data.password, get_user.password):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Information invalide"
        )
    access_token = oauth2.create_access_token({"user_id": get_user.id, "email": get_user.email, "username": get_user.nom})
    return {"access_token": access_token, "token_type": "bearer"}
    