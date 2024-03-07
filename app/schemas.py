from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union
from datetime import date, datetime, time


class User(BaseModel):
    nom: str = Field(default="Doe")
    prenom: Optional[str] = None
    email: EmailStr = Field(default="example@gmail.com")
    password: str
    
    
class Todo(BaseModel):
    nom_todo: str
    debut_todo: Optional[datetime] = None
    fin_todo: Optional[datetime] = None
    
# classes de creation

class CreateUser(User):
    pass

class CreateTodo(Todo):
    date_modif_todo: Optional[datetime] = None
    user_id: Optional[int] = None
    pass

# classes des reponses

class TodoResponse(BaseModel):
    id: int
    nom_todo: str
    debut_todo: Union[datetime, None]
    fin_todo: Union[datetime, None]
    date_ajout_todo: datetime
    date_modif_todo: datetime
    user_id: Optional[int]
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: Optional[str] = None
    email: EmailStr
    date_ajout: datetime
    date_modif: datetime
    class Config:
        from_attributes = True
    
# classes de mise a jour
class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    date_modif: Optional[datetime] = None
    
class LoginUser(BaseModel):
    username: str
    password: str
    
    
# token schema

class TokenData(BaseModel):
    id: int
    email: EmailStr
    username: str