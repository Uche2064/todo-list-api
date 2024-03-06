from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from .. import db, models, schemas
from pydantic import EmailStr
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/todo",
    tags=["Todos"]
)

@router.get("/{email}", response_model=List[schemas.TodoResponse])
async def get_todos(email: EmailStr, db: Session = Depends(db.get_db)):
    # verifier si l'utilisateur existe
    get_user = db.query(models.User).filter(models.User.email == email).first()
    # si non, envoyer un message d'erreur et le renvoyer vers la partie creation
    if get_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Utilisateur non trouvé")
    user_todos = db.query(models.Todo).filter(models.Todo.user_id == get_user.id)
    # si oui, recuperer ses todo
    return user_todos

@router.post("/{email}", status_code=status.HTTP_201_CREATED, response_model=schemas.TodoResponse)
async def create_todo(todo: schemas.CreateTodo, email: EmailStr, db: Session = Depends(db.get_db)):
    get_user = db.query(models.User).filter(models.User.email == email).first()
    if get_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    new_todo = models.Todo(**todo.model_dump())
    new_todo.user_id = get_user.id
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return new_todo

@router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TodoResponse)
async def modifier_todo(id: int, todo: schemas.CreateTodo, db: Session = Depends(db.get_db)):
    get_todo = db.query(models.Todo).filter(models.Todo.id == id)
    if get_todo.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tâche non trouvé")
    todo.date_modif_todo = datetime.now()
    get_todo.update(todo.model_dump(), synchronize_session=False)
    
    return get_todo.first()