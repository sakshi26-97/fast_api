# run command uvicorn app.main:app --reload

import uvicorn #for debugging
from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute
from .routers import urls
from .middlewares.auth import auth_middleware
#  verify_auth

#
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
#



tags_metadata = [
    {
      "name": "test",
      "description": "Operations with API to test deployment",
      "externalDocs": {
        "description": "Deployment Docs",
        "url": "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
      }
    },
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
    }
]

app = FastAPI(
  title="Acc",
  description="Tool",
  version="2.5.0",
  openapi_tags=tags_metadata
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:8000"
    "http://127.0.0.1:8000"
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
  # allow_origin_regex="https://.*\.example\.org"
  # max_age=600 (600 default)
)

app.mount("/static", StaticFiles(directory="static"), name="static")

"""
if app is needed in auth.py file then pass it, otherwise not needed
"""
# app.middleware("http")(auth_middleware(app))
# app.middleware("http")(verify_auth)

"""
Enforces that all incoming requests must either be https or wss
"""
# app.add_middleware(HTTPSRedirectMiddleware)

"""
Enforces that all incoming requests have a correctly set Host header, in order to guard against HTTP Host Header attacks.
If an incoming request does not validate correctly then a 400 response will be sent.
"""
# app.add_middleware( TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"])

"""
Handles GZip responses for any request that includes "gzip" in the Accept-Encoding header.
The middleware will handle both standard and streaming responses.
minimum_size - Do not GZip responses that are smaller than this minimum size in bytes. Defaults to 500.
"""
# app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  return PlainTextResponse(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

app.include_router(urls.router, prefix="/api/v1")

@app.get("/", tags=["test"])
async def read_main():
  """
    Dummy API to test the deployment
  """
  return {
    "msg": "Hello World"
  }


def get_route_names(app: FastAPI) -> None:
  for route in app.routes:
    if isinstance(route, APIRoute):
      print(route, route.name, route.operation_id)

# get_route_names(app)

# TO-DO
# Dependencies and Adv Dependencies
#Oauth2
# multiple request body
# files, Form data
# background_tasks
# patch and delete

# fake_secret_token = "coneofsilence"

# async def get_token_header(x_token: str = Header(...)):
#   if x_token != "fake-super-secret-token":
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Token header invalid")

# @app.get("/")
# async def read_main(x_token: str = Header(...)):
#   if x_token != fake_secret_token:
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid x_token header")
#   return {
#     "msg": "Hello World"
#   }

# app.include_router(users.router)
# # Having dependencies in a decorator can be used, for example, to require authentication for a whole group of path operations. Even if the dependencies are not added individually to each one of them.
# app.include_router(
#   items.router,
#   prefix="/items",
#   tags=["items"],
#   dependencies=[Depends(get_token_header)],
#   responses={404: {"description": "Not Found"}})

#for debugging
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)