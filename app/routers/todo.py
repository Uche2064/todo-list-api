from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from .. import db, models, schemas, oauth2
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/todo",
    tags=["Todos"]
)

@router.get("/", response_model=List[schemas.TodoResponse])
async def get_todos(get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), db: Session = Depends(db.get_db)):
    # verifier si l'utilisateur existe
    get_user = db.query(models.User).filter(models.User.email == get_current_user.email).first()
    # si non, envoyer un message d'erreur et le renvoyer vers la partie creation
    if get_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Utilisateur non trouvé")
    user_todos = db.query(models.Todo).filter(models.Todo.user_id == get_user.id).all()
    # si oui, recuperer ses todo
    return user_todos

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TodoResponse)
async def create_todo(
    todo: schemas.CreateTodo, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), 
    db: Session = Depends(db.get_db)):
    
    get_user = db.query(models.User).filter(models.User.email == get_current_user.email).first()
    if get_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    new_todo = models.Todo(**todo.model_dump())
    new_todo.user_id = get_user.id
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return new_todo

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    id: int, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)):
    get_todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == get_current_user.id)
    if get_todo.first() is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Tâche non trouvé"
        )
    get_todo.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TodoResponse)
async def update_todo(
    id: int, 
    todo: schemas.CreateTodo, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)):
    get_todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == get_current_user.id)
    if get_todo.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tâche non trouvé")
    todo.date_modif_todo = datetime.now()
    todo.user_id = get_current_user.id
    get_todo.update(todo.model_dump(), synchronize_session=False)
    db.commit()
    return get_todo.first()
