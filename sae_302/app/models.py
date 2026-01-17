from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app import db

# initialisation des modeles recuperant les informations de la base de donnees nécessaires
class Users(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(45), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, nullable=False)

class Machines(db.Model):
    __tablename__ = "machines"
    nom: Mapped[str] = mapped_column(String(100), primary_key=True)
    IP: Mapped[str] = mapped_column(String(45), nullable=False)

class Role(db.Model):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    privilege: Mapped[int] = mapped_column(Integer, nullable=False)