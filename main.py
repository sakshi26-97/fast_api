from typing import Optional, List, Dict, Set, Union #data-types
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, Form, File, UploadFile, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
  http_exception_handler, request_validation_exception_handler
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
#Pydantic is a library for data validation and settings management based on Python type hinting and variable annotations. You can use Pydantic for defining schemas of complex structures in Python.
from pydantic import BaseModel, Field, HttpUrl, EmailStr
# uvicorn - for the server that loads and serves your application.
from datetime import date, datetime, timedelta, time
import time as Time
from enum import Enum
from uuid import UUID

# to generate and verify the JWT tokens in Python
from jose import JWTError, jwt
# handle password hashes
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = ".."
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The order of each tag metadata dictionary also defines the order shown in the docs UI. user will come before items. Default alphabetical
tags_metadata = [
    {
        "name": "user",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
      "name": "test",
      "description": "Operations with API to test deployment",
      "externalDocs": {
        "description": "Deployment Docs",
        "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
      }
    }
]

app = FastAPI(
  title="FastAPI documentation",
  description="This is a very fancy project, with auto docs for the API and everything",
  version="2.5.0",
  openapi_tags=tags_metadata,
  # openapi_url="/api/v1/openapi.json",
  # docs_url="/api/v1/docs",
  # redoc_url="/api/v1/redoc"

) #app variable will be an "instance" of the class FastAPI

# "Mounting" means adding a complete "independent" application in a specific path, that then takes care of handling all the sub-paths.
app.mount("/static", StaticFiles(directory="static"), name="static")

###############CORS###########
origins = [
  "http://localhost:8000",
  "http://127.0.0.1:8000"
]
# or origins = ["*"], "*" --> wildcard

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
  # allow_origin_regex,
  # expose_headers --> Indicate any response headers that should be made accessible to the browser. Defaults to []
  # max_age --> Sets a maximum time in seconds for browsers to cache CORS responses. Defaults to 600.
)




# A Pydantic Image model which is submodel of Item model
class Image(BaseModel):
  url: HttpUrl
  name: str

# A Pydantic Item model
class Item(BaseModel):
  name: str
  price: float = Field(..., gt=0, description="The price must be greater than zero")
  is_offer: Optional[bool] = None
  description: Optional[str] = Field(None, description="The description of the item", max_length=300)
  tax: Optional[float] = None
  tags: Set[str] = set()
  image: Optional[List[Image]] = None  #Nested Models

  class Config:
    schema_extra = {
        "example": {
            "name": "Foo",
            "price": 35.4,
            "is_offer": 1,
            "description": "A very nice Item",
            "tax": 3.2,
            "tags": [
              "rock",
              "metal",
              "bar"
            ],
            "images": [
                {
                    "url": "http://example.com/baz.jpg",
                    "name": "The Foo live"
                },
                {
                    "url": "http://example.com/dave.jpg",
                    "name": "The Baz"
                }
            ]
        }
    }

# A Pydantic User model
class User(BaseModel):
  name: str = Field(..., example="Foo")
  joined: date
  friends: List[str] = []

# A Pydantic UserBase model
class UserBase(BaseModel):
  username: str
  email: EmailStr
  full_name: Optional[str] = None

# A Pydantic UserIn model that extends UserBase Model
class UserIn(UserBase):
  password: str

# A Pydantic UserOut model that extends UserBase Model
class UserOut(UserBase):
  pass

# A Pydantic UserInDB model that extends UserBase Model
class UserInDB(UserBase):
  hashed_password: str

class ModelName(str, Enum):
  """ values must be of type string """
  alexnet = "alexnet"
  resnet = "resnet"
  lenet = "lenet"

class BaseItem(BaseModel):
  description: str
  type: str

class CarItem(BaseItem):
  type: "car"

class PlaneItem(BaseItem):
  type: "plane"
  size: int

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  username: Optional[str] = None

##################Exception Handler#################
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
  print(f"OMG! An HTTP error!: {repr(exc)}")
  return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  # return JSONResponse(status_code=400, content={
  #   "exception": str(exc)
  # })
  # return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder({
  #   "detail": exc.errors(),
  #   "body": exc.body
  # }))
  print(f"OMG! The client sent invalid data!: {exc}")
  return await request_validation_exception_handler(request, exc)


##################Dependency Injection#################
# *********Dependency Injection as Function**********
async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
  return {
    "q": q,
    "skip": skip,
    "limit": limit
  }

# *********Dependency Injection as Class**********
class CommonQueryParameters():
  """
    Dependency Injection as Class provides support of data types
  """
  def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
    self.q = q
    self.skip = skip
    self.limit = limit

# *********Sub-Dependencies**********
def query_extractor(q: Optional[str] = None):
  return q

def query_or_cookie_extractor(q: str = Depends(query_extractor), last_query: Optional[str] = Cookie(None)):
  if not q:
    print("last_query", last_query)
    return last_query
  return q


# *********Dependency Injection without return **********
async def verify_token(x_token: str = Header(...)):
  if x_token != "fake-super-secret-token":
    raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
  if x_key != "fake-super-secret-key":
    raise HTTPException(status_code=400, detail="X-Key header invalid")
  return x_key


# *********Dependency Injection with yield **********
async def get_db():
  """
    Only the code prior to and including the yield statement is executed before sending a response.
    The code following the yield statement is executed after the response has been delivered
  """
  db = DBSession()
  try:
    yield db
  finally:
    db.close()


#****************OAuth2PasswordBearer*******
"""
  tokenUrl is the url where token can be generated
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")




# Supporting functions
def fake_password_hasher(raw_password: str):
  """
    hashed password cannot be recovered back
  """
  return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
  hashed_password = fake_password_hasher(user_in.password)
  user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
  # **user_in.dict(exclude_unset=True) ==> to exclude unset parameters
  print("User saved! ..not really")
  return user_in_db

def fake_decode_token(token):
  return UserBase(
    username=token+"fakedecoded",
    email="john@example.com",
    full_name="John Doe"
  )

def get_current_user(token: str = Depends(oauth2_scheme)):
  user = fake_decode_token(token)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
          )
  return user


def get_password_hash(password):
  return pwd_context.hash(password)

def verify_password(raw_password, hashed_password):
  return pwd_context.verify(raw_password, hashed_password)

def get_db_user(db, username: str):
  if username in db:
    user_dict = db[username]
    return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
  user = get_db_user(fake_db, username)
  if not user:
    return False
  if not verify_password(password, user.hashed_password):
    return False
  return user







# sample db response
items = {
    1: {"description": "All my friends drive a low rider", "type": "car"},
    2: {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

fake_db = {}

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "supersecretsecret"
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "supersecretsecret2"
    },
}


@app.get("/", tags=["test"])
def read_root(token: str = Depends(oauth2_scheme)):
  """
    OAuth2PasswordBearer used as security for authentication and authorization
  """
  return {
    "Hello": "World",
    "token": token
  }

@app.get("/ping", response_model=Dict[str, str])
async def read_ping():
  """ If your code uses async / await, use async def """
  return {
    "ping": "pong"
  }

# @app.get("/item/{item_id}", response_model=Union[PlaneItem, CarItem])
# def read_item(item_id: int):
#   '''
#      Union[PlaneItem, CarItem] ==> that means, that the response would be any of the two types
#      The most specific type should appear first, followed by the less specific type
#       In the example, the more specific PlaneItem comes before CarItem in Union[PlaneItem, CarItem]
#   '''
#   return items[item_id]

@app.get("/items/{item_id}", tags=["items"])
def read_item(*, item_id: int, q: str = Query(..., min_length=3), ads_id: Optional[str] = Cookie(None), skip: int = 0, limit: int, user_agent: Optional[str] = Header(None)):
  '''
    q is required with min length = 3,
    * "*" as first parameter in function argument will let know that all the following parameters should be called as keyword arguments (key-value pairs), also known as kwargs. Even if they don't have a default value. Otherwise Python will complain if you put a value with a "default" before a value that doesn't have a "default".
    * user_agent and ads_id appear in headers in request body
    * by default, Header will convert the parameter names characters from underscore (_) to
      hyphen (-) to extract and document the headers as most of the standard headers are separated by a "hyphen" character but a variable like user-agent is invalid in Python.
    * If for some reason you need to disable automatic conversion of underscores to hyphens,
      set the parameter "convert_underscores" of Header to False:
  '''
  if item_id not in items:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found", headers={"X-Error": "There goes my error"})
  return {
    "item_id": item_id,
    "q": q
  }

@app.put("/items/{item_id}",  tags=["items"])
def update_item(item_id: int, item: Item, q: Optional[str] = None):
  """
    FastAPI will recognize that the function parameters that match path parameters should be taken from the path, and that function parameters that are declared to be Pydantic models should be taken from the request body and other as query parameters.
    ***item.dict() --> retruns all data of Item model
  """
  response = {
    "item_id": item_id,
    **item.dict()
  }
  if q:
    # response.update({
    #   "q": q
    # })

    # OR
    response["q"] = q
  return response
  # return {
  #   "item_id": item_id,
  #   "item_name": item.name,
  #   "item_price": item.price
  # }


@app.patch("/items/{item_id}", tags=["items"])
def update_specific_item(*, item_id: int = Path(..., title="The id of the item to update", ge=0,
  le=10, description="Id for the items to search in the database that have a good match"),
  q: Optional[List[str]] = Query(None, min_length=3, max_length=50, title="Query String", description="Query string for the items to search in the database that have a good match", alias="item-query", deprecated=True), item: Item):
  """
    Query prameter list/ multiple values 'q: Optional[List[str]]'
    * **jsonable_encoder**
      - There are some cases where you might need to convert a data type (like a Pydantic model) to something compatible with JSON (like a dict, list, etc). For example, if you need to store it in a database.
  """
  json_compatible_item_data = jsonable_encoder(item)
  fake_db[item_id] = json_compatible_item_data
  return {
    "item_id": item_id
  }

@app.get("/items", tags=["items"])
def list_item(item_id: UUID, start_datetime: Optional[datetime] = Body(None), end_datetime: Optional[datetime] = Body(None), repeat_at: Optional[time] = Body(None), process_after: Optional[timedelta] = Body(None)):
  start_process = start_datetime + process_after
  duration = end_datetime - start_process
  return {
      "item_id": item_id,
      "start_datetime": start_datetime,
      "end_datetime": end_datetime,
      "repeat_at": repeat_at,
      "process_after": process_after,
      "start_process": start_process,
      "duration": duration,
  }

@app.post("/items", response_model=Item, response_model_exclude_unset=True, status_code=status.HTTP_201_CREATED, tags=["items"])
def create_item(item: Item):
  """
    _response_model_exclude_unset=True_ will omit the key-value pairs from the result if they have default values or the one which are not actually stored
    * want to exclude only defaults then use 'response_model_exclude_defaults=True'
    * want to exclude only None then use 'response_model_exclude_none=True'
    * want to include specific attributes from response_model use 'response_model_include' example 'response_model_include={"name", "description"}'
    * want to exclude specific attributes from response_model use 'response_model_exclude'
    * status code "HTTP_201_CREATED" will be used in the response and will be added to the OpenAPI schema
  """
  return item


##############USER################
@app.get('/user/me', tags=["user"])
def read_user_me(current_user: UserBase = Depends(get_current_user)):
  return current_user


@app.get('/user/{user_id}', tags=["user"])
def get_user(user_id: UUID = Path(..., example="123e4567-e89b-12d3-a456-426614174000"), user_name: Optional[str] = Query(None, min_length=3, max_length=50)):
  """
    username is optional with max length of user_name is 50 and min_length is 3
  """
  return {
    "user_id": user_id,
    "user_name": user_name,
  }

@app.put('/user/{user_id}',  tags=["user"])
def update_user(user_id: int, user_details: User = Body(..., embed=True)):
  """
    Due to embed, the request body will be of the form { "user" : {
      "name": str
      "joined": date
      "friends": List[str] = []
    }}
    instead of {
      name: str
      joined: date
      friends: List[str] = []
    }
  """
  return {
    "user_id": user_id,
    "user_name": user_details.name,
    "joined_date": user_details.joined,
    "friends": user_details.friends
  }

@app.patch("/items/{item_id}/users/{user_id}", tags=["items"])
def update_user_items(item_id: int, user_id: int, item: Item, user: User, importance: int = Body(..., gt=0, example=12), q: Optional[str] = None):
  """
    Multiple body parameters - User and Item, and additional body parameter "importance" instead of query parameter
  """
  return {
    "item_id": item_id,
    "user_id": user_id,
    "item_name": item.name,
    "user_name": user.name,
    "importance": importance
  }

############## UserIn ################
# Don't do this in production!
@app.post("/user/", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["user"])
async def create_user(user: UserIn):
  """
    The returned user will have response_model to be our model UserOut, that doesn't include the password
  """
  user_saved = fake_save_user(user)
  return user_saved


##############MODEL################
@app.get("/model/{model_name}", tags=["model"])
async def get_model(model_name: ModelName):
  """
    Enum example
  """
  print(model_name, model_name.value, ModelName.alexnet.value)
  if model_name == ModelName.alexnet:
    return {
      "model_name": model_name,
      "message": "Deep Learning FTW!"
    }
  elif model_name.value == "lenet":
    return {
      "model_name": model_name,
      "message": "LeCNN all the images"
    }
  return {
    "model_name": model_name,
    "message": "Have some residuals"
  }

##############Path parameters containing paths################
@app.get("/files/{file_path:path}", tags=["files"])
async def read_file(file_path: str = Path(..., example="/home/johndoe/myfile.txt")):
  """
    if file_path == /home/johndoe/myfile.txt then
    endpoint path --> /files//home/johndoe/myfile.txt
  """
  return {"file_path": file_path}

##############Images################
@app.post("/images/multiple/", tags=["images"], deprecated=True)
async def create_multiple_images(images: List[Image]):
    return images

#####################Form Data################
@app.post("/login/token", tags=["login"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
  """
    UserInDB(**user_dict) means:
    Pass the keys and values of the user_dict directly as key-value arguments, equivalent to:
    UserInDB(
        username = user_dict["username"],
        email = user_dict["email"],
        full_name = user_dict["full_name"],
        hashed_password = user_dict["hashed_password"]
    )
  """
  user_dict = fake_users_db.get(form_data.username) #since fake_users_db is dict so it returns dict
  print("user_dict", user_dict)
  if not user_dict:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
  user = UserInDB(**user_dict)
  print("user", user)
  hashed_password = fake_password_hasher(form_data.password)
  if not hashed_password == user.hashed_password:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
  return {"access_token": user.username, "token_type": "bearer"}


@app.post("/login/", tags=["login"])
def login(username: str = Form(...), password: str = Form(...)):
  """
    When you need to receive form fields instead of JSON, you can use Form.
    You can declare multiple Form parameters in a path operation, but you can't also declare Body fields that you expect to receive as JSON, as the request will have the body encoded using application/x-www-form-urlencoded instead of application/json.
    * Header --> "Content-Type: application/x-www-form-urlencoded"
    * File, UploadFile, Form can be declared, Example -> (file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...))
  """
  return {"username": username}

#####################Request File################
@app.post("/files/")
async def create_file(file: bytes = File(...), tags=["files"]):
  """
    To declare File bodies, you need to use File, because otherwise the parameters would be interpreted as query parameters or body (JSON) parameters.
    * This will work well for small files. Instead use "UploadFile"
    * Header --> "Content-Type: multipart/form-data"
    * file are passed as '-F "file=@EM_PayStub_PDF__0.jpg;type=image/jpeg' in curl command
  """
  return {
    "file_size": len(file)
  }

@app.post("/files/uploadfile/", tags=["files"])
async def create_upload_file(file: UploadFile = File(...)):
  """
    work well for large files like images, videos, large binaries, etc. without consuming all the memory.
    * You can get metadata from the uploaded file
    * Header --> "Content-Type: multipart/form-data"
    * file are passed as '-F "file=@EM_PayStub_PDF__0.jpg;type=image/jpeg' in curl command
    * UploadFile has the following attributes
      - **filename**: A str with the original file name that was uploaded (e.g. myimage.jpg).
      - **content_type**: A str with the content type (MIME type / media type) (e.g. image/jpeg).
      - **file**: A SpooledTemporaryFile (a file-like object). This is the actual Python file that you can pass directly to other functions or libraries that expect a "file-like" object.
  """
  return {
    "file_name": file.filename
  }

@app.post("/files/multipleUploadFile/", tags=["files"], summary="upload multiple files using UploadFile feature", description='Multiple files can be uploaded using "List[UploadFile]', response_description="the uploaded multiple files")
async def create_multiple_upload_file(files: List[UploadFile] = File(...)):
  """
    This thing work same as description in decorator
    * Multiple files can be uploaded using "List[UploadFile]
  """
  return {
    "file_name": [{
      "file_name": file.filename,
      "content_type": file.content_type
    } for file in files]
  }

#####################Custom Exception Handlers################
class UnicornException(Exception):
  def __init__(self, name):
    self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
  return JSONResponse(status_code=418, content={
    "message": f"Oops! {exc.name} did something. There goes a rainbow..."
  })

@app.get("/unicorns/{name}", tags=["unicorns"])
async def read_unicorn(name: str):
  if name == "yolo":
    raise UnicornException(name=name)
  return {
    "unicorn_name": name
  }

#####################Projects (Using Dependency Injection)################
@app.get("/projects/read_query", tags=["projects"])
def read_project_query(query_or_default: str = Depends(query_or_cookie_extractor)):
  """
    Example of subdependcy injection
  """
  return {
    "q_or_cookie": query_or_default
  }

@app.get("/tasks/verify_headers", tags=["tasks"], dependencies=[Depends(verify_token), Depends(verify_key)])
def verify_task_headers():
  """
    Example of list of dependencies to the path operation decorator
  """
  return {"task": "Foo"}

@app.get("/projects/{project_id}", tags=["projects"])
def get_project(project_id: int, commons: dict = Depends(common_parameters)):
  """
    common_parameters declared once as function and used as dependency injection in projects and tasks
  """
  return commons

@app.get("/tasks/{task_id}", tags=["tasks"])
def get_task(task_id: int, commons: dict = Depends(common_parameters)):
  """
    common_parameters declared once as function and used as dependency injection in projects and tasks
  """
  return commons


@app.put("/projects/{project_id}", tags=["projects"])
def get_project(project_id: int, commons: CommonQueryParameters = Depends(CommonQueryParameters)):
  """
    common_parameters declared once as Class and used as dependency injection in projects and tasks
  """
  return commons

@app.put("/tasks/{task_id}", tags=["tasks"])
def get_task(task_id: int, commons: CommonQueryParameters = Depends()):
  """
    common_parameters declared once as Class and used as dependency injection in projects and tasks.
    **shortcut** - You declare the dependency as the type of the parameter, and you use Depends() as its "default" value (that after the =) for that function's parameter, without any parameter in Depends(), instead of having to write the full class again inside of Depends(CommonQueryParams).
  """
  return commons


##################Middleware###############
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
  """
    A "middleware" is a function that works with every request before it is processed by any specific path operation. And also with every response before returning it
    - If you have dependencies with yield, the exit code will run after the middleware.
    - If there were any background tasks, they will run after all the middleware.
    The middleware function receives
    - request
    - A function call_next that will receive the request as a parameter
    * This function will pass the request to the corresponding path operation.
    * Then it returns the response generated by the corresponding path operation.
    - The response can be modified further before returning it.
    Custom proprietary headers can be added using the 'X-' prefix
  """
  start_time = Time.time()
  response = await call_next(request)
  process_time = Time.time() - start_time
  # JSON object doesn't support datetime hence need to convert it into string
  response.headers["X-Process-Time"] = str(process_time)
  return response


##################Background Tasks and as dependency###############
def write_notification(email: str, message=""):
  with open("log.txt", mode="w") as email_file:
    content = f"notification for {email}: {message}"
    email_file.write(content)

def write_log(message: str):
  with open("log.txt", mode="a") as log:
    log.write(message)

def get_query(background_tasks: BackgroundTasks, q: Optional[str] = None):
  if q:
    message = f"found query: {q}\n"
    background_tasks.add_task(write_log, message)
  return q

@app.post("/send-notification/{email}", tags=["send-notification"])
async def send_notification(email: str, background_tasks: BackgroundTasks):
    """
    You can define background tasks to be run after returning a response
    This is useful for operations that need to happen after a request, but that the client doesn't really have to be waiting for the operation to complete before receiving the response
    **.add_task() receives as arguments:**
    - A task function to be run in the background (write_notification).
    - Any sequence of arguments that should be passed to the task function in order (email).
    - Any keyword arguments that should be passed to the task function (message="some notification").
    """
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}

@app.post("/send-notifications/{email}", tags=["send-notification"])
async def send_notification_dependency(email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)):
    """
      Using BackgroundTasks also works with the dependency injection system, you can declare a parameter of type BackgroundTasks at multiple levels: in a path operation function, in a dependency (dependable), in a sub-dependency, etc.

      FastAPI knows what to do in each case and how to re-use the same object, so that all the background tasks are merged together and are run in the background afterwards:
    """
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}