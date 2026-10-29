import json

import pytest

from app.api import events_crud as crud

EVENT = {"title": "Jazz Night", "city": "Paris", "price_usd": 25.0, "seats_left": 100}


def test_create_event(test_app, monkeypatch):
    async def mock_post(payload):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/events/", content=json.dumps(EVENT))
    assert response.status_code == 201
    assert response.json() == {"id": 1, **EVENT}


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Jazz Night"},
        {**EVENT, "title": "ab"},
        {**EVENT, "city": "P"},
        {**EVENT, "price_usd": -1},
        {**EVENT, "seats_left": -1},
    ],
)
def test_create_event_invalid(test_app, payload):
    response = test_app.post("/events/", content=json.dumps(payload))
    assert response.status_code == 422


def test_read_event(test_app, monkeypatch):
    async def mock_get(id):
        return {"id": 1, **EVENT}

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/events/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **EVENT}


def test_read_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.get("/events/0/")
    assert response.status_code == 422


def test_read_all_events(test_app, monkeypatch):
    test_data = [{"id": 1, **EVENT}, {"id": 2, **EVENT, "city": "Rome"}]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud, "get_all", mock_get_all)

    response = test_app.get("/events/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_update_event(test_app, monkeypatch):
    async def mock_get(id):
        return True

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(crud, "get", mock_get)
    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/events/1/", content=json.dumps(EVENT))
    assert response.status_code == 200
    assert response.json() == {"id": 1, **EVENT}


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {**EVENT, "title": "ab"}, 422],
        [1, {**EVENT, "price_usd": -5}, 422],
        [0, EVENT, 422],
        [999, EVENT, 404],
    ],
)
def test_update_event_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/events/{id}/", content=json.dumps(payload))
    assert response.status_code == status_code


def test_remove_event(test_app, monkeypatch):
    async def mock_get(id):
        return {"id": 1, **EVENT}

    async def mock_delete(id):
        return id

    monkeypatch.setattr(crud, "get", mock_get)
    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **EVENT}


def test_remove_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.delete("/events/0/")
    assert response.status_code == 422
