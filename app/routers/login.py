from typing import List
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from app.models.users import UserIn, UserInDB, UserOut, fake_users_db

from jose import JWTError, jwt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def generate_hashed_password(raw_password: str):
    return pwd_context.hash(raw_password)

def verify_password(raw_password: str, hashed_password: str):
  return pwd_context.verify(raw_password, hashed_password)

@router.post("/")
async def login(username: str = Body(...), password: str = Body(...)):
    """
      Login functionality
    """
    print("username", username, "password", password)
    if username in fake_users_db:
      hashed_password = fake_users_db[username].dict().get("hashed_password")
      if verify_password(generate_hashed_password(password), hashed_password):
        return JSONResponse(content={
          "message": "Login Successful"
        }, status_code=status.HTTP_200_OK)
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
        "message": "Incorrect password"
      })
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
        "message": f"{username} doesnot exist in DB. Unsuccessful Login"
      })