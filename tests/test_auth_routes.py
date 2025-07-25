import pytest

def test_register_success(client, db_session):
    data = {
        "email": "newuser@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "nickname": "johndoe",
        "phone": "+1234567891",
        "password": "Password2"
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200

def test_register_duplicate_email(client, test_user):
    data = {
        "email": "test@example.com",  # Usar mismo email del conftest.py
        "firstname": "John",
        "lastname": "Doe",
        "nickname": "johndoe2",
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
        ("nickname", "", 400),
        ("phone", "", 400),
        ("password", "short", 400),  # Cambiar de 422 a 400
        ("phone", "123456", 400),
        ("firstname", "A"*51, 400),
        ("lastname", "B"*51, 400),
        ("nickname", "C"*31, 400),  # Reducir a 31 caracteres para que falle la validación
    ]
)
def test_register_invalid_fields(client, field, value, expected_status):
    data = {
        "email": "invalid@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "nickname": "testuser123",
        "phone": "+1234567899",
        "password": "Password2"
    }
    data[field] = value
    response = client.post("/auth/register", json=data)
    assert response.status_code == expected_status

def test_login_success(client, test_user):
    data = {
        "email": "test@example.com",  # Usar mismo email del conftest.py
        "password": "Password1"
    }
    response = client.post("/auth/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, test_user):
    data = {
        "email": "test@example.com",
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
    data = {"email": "test@example.com"}
    response = client.post("/auth/request-email-verification", json=data)
    assert response.status_code == 200
    assert "Verification email sent" in response.json()["msg"]

def test_request_email_verification_user_not_found(client):
    data = {"email": "nouser@example.com"}
    response = client.post("/auth/request-email-verification", json=data)
    assert response.status_code == 404

def test_request_password_reset_success(client, test_user):
    data = {"email": "test@example.com"}
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