from fastapi import FastAPI
from .db import Base, engine
from . import models
from .routers import users, todo

app = FastAPI()

try: 
    models.Base.metadata.create_all(bind=engine)
    print("Connexion réussie")
except Exception as e:
    print(e)
    exit
    
app.include_router(users.router)
app.include_router(todo.router)