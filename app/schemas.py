from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime, time


class User(BaseModel):
    nom: str = Field(default="Doe")
    prenom: Optional[str] = None
    email: EmailStr = Field(default="example@gmail.com")
    
    
class Todo(BaseModel):
    nom_todo: str
    debut_todo: date
    temps_debut: time
    fin_todo: date
    temps_fin: time
    
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
    debut_todo: date
    temps_debut: time
    fin_todo: date
    temps_fin: time
    date_modif_todo: datetime
    date_ajoute_todo: datetime
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: Optional[str] = None
    email: EmailStr
    date_ajoute: datetime
    date_modif: datetime
    class Config:
        from_attributes = True
    
# classes de mise a jour
class UserUpdate(User):
    date_modif: Optional[datetime] = None