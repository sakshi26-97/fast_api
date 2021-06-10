from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

# def test_read_main():
#   """
#     Notice that the testing functions are normal def, not async def.
#     And the calls to the client are also normal calls, not using await.
#     This allows you to use pytest directly without complications.
#     If you want to call async functions in your tests apart from sending requests to your FastAPI application (e.g. asynchronous database functions), use Async Tests
#   """
#   response = client.get("/", headers={"X-Token": "coneofsilence"})
#   assert response.status_code == 200
#   assert response.json() == {"msg": "Hello World"}

# def test_read_main_bad_token():
#   response = client.get("/", headers={"X-Token": "hailhydra"}
#   # to pass body ==> json={}
#   )
#   assert response.status_code == 400
#   assert response.json() == {"detail": "Invalid x_token header"}


def test_list_items():
  response = client.get("/api/v1/items", headers={"Authorization": "Basic ..."})
  assert response.status_code == 200