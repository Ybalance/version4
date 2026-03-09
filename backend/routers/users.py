from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, database, auth

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCreate, db: Session = Depends(database.get_db)):
    print(f"Login attempt for: {user_credentials.phone}") # Debug log
    # Note: reusing UserCreate which has phone/password. Ideally use OAuth2PasswordRequestForm
    user = crud.get_user_by_phone(db, phone=user_credentials.phone)
    if not user:
        print("User not found") # Debug log
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    
    if not auth.verify_password(user_credentials.password, user.hashed_password):
        print("Password mismatch") # Debug log
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    
    access_token = auth.create_access_token(data={"sub": user.phone})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user
