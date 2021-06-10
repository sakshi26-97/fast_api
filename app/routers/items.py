from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.models.items import Item, fake_db_items
router = APIRouter()

@router.get("/", response_model=List[Item], summary="List of all items in the db", #include_in_schema=False --> will not be included in swagger ui
)
async def list_items():
    """
      Returns all the items from the db
      \f
      {Rest of the lines after "\f" won't be visible in swagger ui}
      :param item: User input.
    """
    items_list = []
    count = 0
    for item in fake_db_items:
      print("item", item, fake_db_items[item])
      items_list.append(fake_db_items[item])
      count = count+1
    # return [{"name": "Item Foo"}, {"name": "item Bar"}]
    return JSONResponse(status_code=status.HTTP_200_OK, content={
      "count": count,
      "results": items_list
    })

@router.get("/{item_id}", response_model=Item, operation_id="some_specific_id_you_define")
async def read_item(item_id: int, request: Request):
    """
      Returns the specific item from the db
      operationId is an optional unique string used to identify an operation. If provided, these IDs must be unique among all operations described in your API.
      \n
      **if you get data from the Request object directly (for example, read the body) it won't be validated, converted or documented**
      \n
      Some common use cases for operationId are:
      - Some code generators use this value to name the corresponding methods in code
      - **operation_id --> can be visible in url**
      
    """
    if item_id not in fake_db_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item id {item_id} doesnot exist in database")
    client_host = request.client.host
    print("client_host", client_host)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
      **fake_db_items[item_id],
      "client_host": client_host
    })

@router.post("/")
async def create_items(item: Item):
    """
      Insert new item in the db
    """
    max_item_id = 0
    for item_id in fake_db_items:
      if item_id > max_item_id:
        max_item_id = item_id
    item_saved = Item(**item.dict())
    fake_db_items[max_item_id+1] = item_saved
    print("db changes after using Item(**item.dict()) item_saved\n", item_saved)
    fake_db_items[max_item_id+1] = jsonable_encoder(item)
    print("============")
    print("db changes after item creation", fake_db_items)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={
      "message": f"{item.name} successfully inserted in database"
    })

@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
    response_model=Item
)
async def update_item(item_id: int, item: Item):
    """
      Update the specific item in the db
    """
    if item_id not in fake_db_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{item_id} doesnot exist in database")
    fake_db_items[item_id] = item
    return fake_db_items[item_id]


# @app.patch("/items/{item_id}", response_model=Item)
# async def update_item(item_id: str, item: Item):
#     stored_item_data = items[item_id]
#     stored_item_model = Item(**stored_item_data)
#     update_data = item.dict(exclude_unset=True)
#     updated_item = stored_item_model.copy(update=update_data)
#     items[item_id] = jsonable_encoder(updated_item)
#     return updated_item
# @router.patch(
#     "/{item_id}"
# )
# async def partial_update_item(item_id: int, item: Item):
#     if item_id not in fake_db_items:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item id {item_id} doesnot exist in database")
#     fake_db_items[item_id] = item
#     return fake_db_items[item_id]