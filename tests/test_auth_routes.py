import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password
from app.models.user_model import User
from app.db.session import engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        firstname="Test",
        lastname="User",
        email="testuser@example.com",
        hashed_password=hash_password("Password1"),
        user_rol="customer",
        phone="+1234567890"
    )
    db_session.add(user)
    db_session.commit()
    yield user

def test_register_success(client, db_session):
    data = {
        "email": "newuser@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "+1234567891",
        "password": "Password2"
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_duplicate_email(client, test_user):
    data = {
        "email": "testuser@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "+1234567890",
        "password": "Password2"
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@pytest.mark.parametrize(
    "field,value,expected_status",
    [
        ("email", "", 422),
        ("firstname", "", 400),
        ("lastname", "", 400),
        ("phone", "", 400),
        ("password", "short", 422),
        ("phone", "123456", 400),
        ("firstname", "A"*51, 400),
        ("lastname", "B"*51, 400),
    ]
)
def test_register_invalid_fields(client, field, value, expected_status):
    data = {
        "email": "invalid@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "+1234567899",
        "password": "Password2"
    }
    data[field] = value
    response = client.post("/auth/register", json=data)
    assert response.status_code == expected_status

def test_login_success(client, test_user):
    data = {
        "email": "testuser@example.com",
        "password": "Password1"
    }
    response = client.post("/auth/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, test_user):
    data = {
        "email": "testuser@example.com",
        "password": "Wrongpass1"
    }
    response = client.post("/auth/login", json=data)
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    data = {
        "email": "nouser@example.com",
        "password": "Password1"
    }
    response = client.post("/auth/login", json=data)
    assert response.status_code == 401

def test_login_invalid_fields(client):
    data = {
        "email": "",
        "password": ""
    }
    response = client.post("/auth/login", json=data)
    assert response.status_code == 422

def test_request_email_verification_success(client, test_user):
    data = {"email": "testuser@example.com"}
    response = client.post("/auth/request-email-verification", json=data)
    assert response.status_code == 200
    assert "Verification email sent" in response.json()["msg"]

def test_request_email_verification_user_not_found(client):
    data = {"email": "nouser@example.com"}
    response = client.post("/auth/request-email-verification", json=data)
    assert response.status_code == 404

def test_request_password_reset_success(client, test_user):
    data = {"email": "testuser@example.com"}
    response = client.post("/auth/request-password-reset", json=data)
    assert response.status_code == 200
    assert "Reset password email sent" in response.json()["msg"]

def test_request_password_reset_user_not_found(client):
    data = {"email": "nouser@example.com"}
    response = client.post("/auth/request-password-reset", json=data)
    assert response.status_code == 404

def test_confirm_email_invalid_token(client):
    data = {"token": "invalidtoken"}
    response = client.post("/auth/confirm-email", json=data)
    assert response.status_code == 400

def test_reset_password_invalid_token(client):
    data = {"token": "invalidtoken", "new_password": "Password2"}
    response = client.post("/auth/reset-password", json=data)
    assert response.status_code == 400

def test_reset_password_same_as_old(client, db_session, test_user):
    from app.crud.auth_crud import create_action_token
    token_obj = create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    data = {"token": token_obj.token, "new_password": "Password1"}
    response = client.post("/auth/reset-password", json=data)
    assert response.status_code == 422

def test_reset_password_success(client, db_session, test_user):
    from app.crud.auth_crud import create_action_token
    token_obj = create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    data = {"token": token_obj.token, "new_password": "Password2"}
    response = client.post("/auth/reset-password", json=data)
    assert response.status_code == 200
    assert "Password reset successfully" in response.json()["msg"]

def test_undo_password_change_invalid_token(client):
    data = {"token": "invalidtoken"}
    response = client.post("/auth/undo-password-change", json=data)
    assert response.status_code == 400

def test_verify_token_invalid(client):
    data = {"token": "invalidtoken"}
    response = client.post("/auth/verify-token", json=data)
    assert response.status_code == 401