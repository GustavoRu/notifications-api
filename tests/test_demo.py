from fastapi import FastAPI
from fastapi.testclient import TestClient

demo_app = FastAPI()

@demo_app.get("/")
def demo_home():
    return{"message": "Hi from demo"}

client = TestClient(demo_app)

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    