from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
import base64

def auth_middleware(app):
  async def verify_auth(request: Request, call_next):
    try:
      headers = request.headers.get("Authorization")
      print("headers", headers)
      if not headers:
        # response = Response(content="User not authorized", status_code=status.HTTP_401_UNAUTHORIZED)
        response = JSONResponse(content={
            "detail": "User not authorized"
          }, status_code=status.HTTP_401_UNAUTHORIZED)
      else:
        base64_credentials = headers.split(" ")[1]
        base64_credentials_bytes = base64_credentials.encode("ascii")
        decoded_credentials_bytes = base64.b64decode(base64_credentials_bytes)
        credentials = decoded_credentials_bytes.decode("ascii").split(":")
        if credentials[0] == "admin" and credentials[1] == "admin1234":
          response = await call_next(request)
        else:
          response = JSONResponse(content={
            "detail": "Incorrect username or password"
          }, status_code=status.HTTP_400_BAD_REQUEST)
    finally:
      pass
    return response
  return verify_auth

# async def verify_auth(request: Request, call_next):
#   try:
#     headers = request.headers.get("Authorization")
#     print("headers", headers)
#     if not headers:
#       # response = Response(content="User not authorized", status_code=status.HTTP_401_UNAUTHORIZED)
#       response = JSONResponse(content={
#           "detail": "User not authorized"
#         }, status_code=status.HTTP_401_UNAUTHORIZED)
#     else:
#       base64_credentials = headers.split(" ")[1]
#       base64_credentials_bytes = base64_credentials.encode("ascii")
#       decoded_credentials_bytes = base64.b64decode(base64_credentials_bytes)
#       credentials = decoded_credentials_bytes.decode("ascii").split(":")
#       if credentials[0] == "admin" and credentials[1] == "admin1234":
#         response = await call_next(request)
#       else:
#         response = JSONResponse(content={
#           "detail": "Incorrect username or password"
#         }, status_code=status.HTTP_400_BAD_REQUEST)
#   finally:
#     pass
#   return response