from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, ORJSONResponse, HTMLResponse
from app.models.users import User, UserIn, UserInDB, UserOut, fake_users_db

from jose import JWTError, jwt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def generate_hashed_password(raw_password: str):
    return pwd_context.hash(raw_password)

# , response_model=List[UserOut]
@router.get("/", response_class=ORJSONResponse)
async def list_users():
    """
      Returns all the users from the db.
      **By default, FastAPI would automatically convert that return value to JSON using the jsonable_encoder**
    """
    return fake_users_db

# @router.get("/self")
# async def read_user_me():
#     return {"username": "fakecurrentuser"}

@router.get("/html", response_class=HTMLResponse)
async def read_user_html():
    """
      Returns HTML Response.
      **response_class** --> _Includes specific response type_ Here, **text/html**
    """
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/{username}", response_model=User,
# , response_model_exclude={"hashed_password"}
)
async def read_user(username: str):
    """
      Returns the specific user from the db
    """
    if username not in fake_users_db:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{username} doesnot exist in database", headers={"X-Error": "There goes my error"})
    return fake_users_db[username]

@router.post("/",
responses={
  201: {
    "description": "Insert new user in database",
    "content": {
      "application/json": {
        "example": {
          "message": "successfully inserted in database"
          },
      },
      # "set-cookie": {
        # add response  cookies in ui
      # }
    },
  },
  404: {
    "description": "Returns 404 status when user already exist in database",
    # "content": {
    #   "application/json": {
    #     "example": {
    #       "detail": "Already exist in database"
    #     }
    #   }
    # }
  }
},
)
async def create_users(user: UserIn):
    """
      Insert new user in the db.
      **When returned a _Response_ or _JSONResponse_ directly its data is not validated, converted (serialized), nor documented automatically**
    """
    if user.username in fake_users_db:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{user.username} already exist in database")
    generated_hashed_password = generate_hashed_password(user.password)
    user_saved = UserInDB(**user.dict(), hashed_password=generated_hashed_password)
    fake_users_db[user.username] = user_saved
    print("after user saved", fake_users_db)
    # Reponse cookies
    response =  JSONResponse(status_code=status.HTTP_201_CREATED, content={
      "message": f"{user.username} successfully inserted in database"
    })
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response

@router.put("/{username}", responses={
    200: {
        "model": User,
        "description": "update user",
    }
  }
)
async def update_item(username: str, user: UserIn):
    """
      Update the specific user in the db
    """
    if username not in fake_users_db:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{username} doesnot exist in database")
    generated_hashed_password = generate_hashed_password(user.password)
    user_saved = UserInDB(**user.dict(), hashed_password=generated_hashed_password)
    fake_users_db[user.username] = user_saved
    print("after user update", fake_users_db)
    return fake_users_db[user.username]
