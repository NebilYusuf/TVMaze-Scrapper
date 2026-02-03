from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_shows():
    response = client.get("/shows?page=1&page_size=5")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

    if data["items"]:
        show = data["items"][0]
        assert "id" in show
        assert "name" in show
        assert "cast" in show

        cast = show["cast"]
        birthdays = [c["birthday"] for c in cast if c["birthday"]]
        assert birthdays == sorted(birthdays, reverse=True)
