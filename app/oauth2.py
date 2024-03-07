from jose import jwt, JWTError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from . import schemas


oauth2_schemes = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "vON2Du4swE8QD7aI0plmnd3MSQpSrM3+qGCOcIeVYvajwy66UReI8ODI3cZuwrm1hjfRNp0RyXdmson2888ibg="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_TIME = 30

def create_access_token(payload: dict):
    to_encode = payload.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 
    
    return  token

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        email: str = payload.get("email")
        username: str = payload.get("username")
        token_data = schemas.TokenData(id=id, email=email, username=username)
    except JWTError as e:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_schemes)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Impossible de valider les informations",
        headers = {"WWW-Authentification": "Bearer"}
    )
    
    return verify_token(token, credentials_exception)