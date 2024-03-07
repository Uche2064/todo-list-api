from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from .. import db, models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import or_

router = APIRouter(
    prefix="/todo",
    tags=["Todos"]
)

# Obtenir toutes les tâches de l'utilisateur actuel
@router.get("/", response_model=List[schemas.TodoResponse])
async def get_todos(
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), 
    db: Session = Depends(db.get_db)
):
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(models.User).filter(models.User.email == get_current_user.email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        # Obtenir toutes les tâches de l'utilisateur
        todos = db.query(models.Todo).filter(models.Todo.user_id == user.id).all()
        return todos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Créer une nouvelle tâche pour l'utilisateur actuel
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TodoResponse)
async def create_todo(
    todo: schemas.CreateTodo, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user), 
    db: Session = Depends(db.get_db)
):
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(models.User).filter(models.User.email == get_current_user.email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
        # Créer une nouvelle tâche associée à l'utilisateur
        todo.user_id = user.id
        new_todo = models.Todo(**todo.model_dump())
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Supprimer une tâche spécifique de l'utilisateur actuel
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    id: int, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)
):
    try:
        # Rechercher la tâche à supprimer
        todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == get_current_user.id).first()
        if todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée")
        # Supprimer la tâche
        db.delete(todo)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Mettre à jour une tâche spécifique de l'utilisateur actuel
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TodoResponse)
async def update_todo(
    id: int, 
    todo: schemas.CreateTodo, 
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    db: Session = Depends(db.get_db)
):
    try:
        # Rechercher la tâche à mettre à jour
        todo_db = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == get_current_user.id).first()
        if todo_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée")
        # Mettre à jour les détails de la tâche
        todo_db.nom_todo = todo.nom_todo
        todo_db.debut_todo = todo.debut_todo
        todo_db.fin_todo = todo.fin_todo
        todo_db.description_todo = todo.description_todo
        todo_db.date_modif_todo = datetime.now()
        db.commit()
        db.refresh(todo_db)
        return todo_db
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
