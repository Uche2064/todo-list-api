from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Date, TIME
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from .db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50))
    email = Column(String(50), nullable=False, unique=True, index=True)
    password = Column(String(256))
    date_ajout = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    date_modif = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)

    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nom_todo = Column(String(256), nullable=False)
    debut_todo = Column(TIMESTAMP)
    fin_todo = Column(TIMESTAMP)
    date_ajout_todo = Column(TIMESTAMP, server_default=text("now()"), nullable=False)
    date_modif_todo = Column(TIMESTAMP, server_default=text("now()"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    owner = relationship("User", back_populates="todos")
    
        