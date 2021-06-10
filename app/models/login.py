from typing import Optional
from pydantic import BaseModel, Field

class Login(BaseModel):
  username: str = Field(..., min_length=6, max_length=50, regex="^[a-zA-Z0-9_-]{5,}$", example="johndoe")
  password: str