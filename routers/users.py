from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import User

router = APIRouter()

@router.get("/")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users

@router.post("/")
def create_user(name: str, interest: str):
    db = SessionLocal()
    new_user = User(name=name, interest=interest)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}
