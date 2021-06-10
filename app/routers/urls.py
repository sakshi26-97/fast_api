from fastapi import APIRouter
from app.routers import users, items, login
router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(login.router, prefix="/login", tags=["login"])
# @router.get("/urls/")
# async def read_urls():
#     return [{"username": "Foo"}, {"username": "Bar"}]