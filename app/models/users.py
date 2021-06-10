from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
  username: str = Field(..., min_length=6, max_length=50,
  # , regex="^[a-zA-Z0-9_-]{5,}$", 
  example="johndoe")
  email: EmailStr = Field(..., example="johndoe@example.com")
  #  = Field(..., regex="^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")
  isActive: bool = True
  full_name: Optional[str] = Field(None, example="John Doe")

class UserIn(User):
  password: str = Field(..., min_length=8)
  # , regex="/^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()_+,.\\\/;':"-]).{8,}$/"

class UserOut(User):
  pass

class UserInDB(User):
  hashed_password: str

fake_users_db = {
  "johndoe": {
      "username": "johndoe",
      "full_name": "John Doe",
      "email": "johndoe@example.com",
      "isActive": True,
      "hashed_password": "supersecretsecret"
  },
  "aliceW": {
      "username": "aliceW",
      "full_name": "Alice Wonderson",
      "email": "alice@example.com",
      "isActive": True,
      "hashed_password": "supersecretsecret2"
  },
}