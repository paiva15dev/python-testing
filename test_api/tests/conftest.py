import pytest
from app import create_app, db
from app.models.user import User
from app.models.task import Task


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.query(Task).delete()
        db.session.query(User).delete()
        db.session.commit()
    yield


@pytest.fixture
def user_payload():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "senha123"
    }


@pytest.fixture
def registered_user(client, user_payload):
    res = client.post("/auth/register", json=user_payload)
    assert res.status_code == 201
    return res.get_json()["user"]


@pytest.fixture
def auth_token(client, user_payload, registered_user):
    res = client.post("/auth/login", json={
        "username": user_payload["username"],
        "password": user_payload["password"]
    })
    assert res.status_code == 200
    return res.get_json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}