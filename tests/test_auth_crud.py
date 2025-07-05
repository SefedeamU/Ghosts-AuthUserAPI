import pytest

from app.core.security import hash_password
from app.crud import auth_crud
from app.models.user_model import User
from app.models.auth_model import ActionToken, PasswordRestoreToken

def test_login_success(db_session, test_user, mocker):
    mocker.patch("app.core.security.verify_password", return_value=True)
    from app.schemas.auth_schema import UserLogin
    login_data = UserLogin(email=test_user.email, password="Password1")
    result = auth_crud.login(db_session, login_data)
    assert result["user"].email == test_user.email
    assert "access_token" in result

def test_login_wrong_password(db_session, test_user, mocker):
    mocker.patch("app.core.security.verify_password", return_value=False)
    from app.schemas.auth_schema import UserLogin
    login_data = UserLogin(email=test_user.email, password="Wrongpass1")
    result = auth_crud.login(db_session, login_data)
    assert result is None

def test_login_user_not_found(db_session):
    from app.schemas.auth_schema import UserLogin
    login_data = UserLogin(email="nouser@example.com", password="Password1")
    result = auth_crud.login(db_session, login_data)
    assert result is None

def test_register_success(db_session):
    user = User(
        firstname="New",
        lastname="User",
        email="newuser@example.com",
        nickname="newuser123",
        hashed_password="Password2",
        user_rol="user",
        phone="+1234567891"
    )
    result = auth_crud.register(db_session, user)
    assert result["user"].email == "newuser@example.com"
    assert result["user"].nickname == "newuser123"
    assert "access_token" in result

def test_get_valid_action_token_found(db_session, test_user, mocker):
    # Crea un token válido
    token = auth_crud.create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    mocker.patch("app.core.security.jwt.decode", return_value={"type": "reset"})
    found = auth_crud.get_valid_action_token(db_session, token.token, "reset")
    assert found is not None
    assert found.token == token.token

def test_get_valid_action_token_expired(db_session, test_user, mocker):
    # Token expirado
    token = auth_crud.create_action_token(
        db_session, test_user.id, "reset", expires_minutes=-1
    )
    mocker.patch("app.core.security.jwt.decode", return_value={"type": "reset"})
    found = auth_crud.get_valid_action_token(db_session, token.token, "reset")
    assert found is None

def test_get_valid_action_token_wrong_type(db_session, test_user, mocker):
    token = auth_crud.create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    mocker.patch("app.core.security.jwt.decode", return_value={"type": "other"})
    found = auth_crud.get_valid_action_token(db_session, token.token, "reset")
    assert found is None

def test_get_valid_action_token_jwt_error(db_session, test_user, mocker):
    token = auth_crud.create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    mocker.patch("app.core.security.jwt.decode", side_effect=Exception)
    found = auth_crud.get_valid_action_token(db_session, token.token, "reset")
    assert found is None

def test_mark_action_token_used(db_session, test_user):
    token = auth_crud.create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    auth_crud.mark_action_token_used(db_session, token.token)
    updated = db_session.query(ActionToken).filter_by(token=token.token).first()
    assert updated.used is True

def test_create_action_token_action(db_session, test_user):
    token = auth_crud.create_action_token(db_session, test_user.id, "reset", expires_minutes=5)
    assert isinstance(token, ActionToken)
    assert token.type == "reset"
    assert token.used is False

def test_create_action_token_restore(db_session, test_user):
    token = auth_crud.create_action_token(
        db_session,
        test_user.id,
        "restore",
        expires_minutes=5,
        use_restore_table=True,
        old_hashed_password="OldPassword1"
    )
    assert isinstance(token, PasswordRestoreToken)
    assert token.old_hashed_password == "OldPassword1"
    assert token.used is False

def test_create_action_token_with_extra_payload(db_session, test_user):
    token = auth_crud.create_action_token(
        db_session,
        test_user.id,
        "reset",
        expires_minutes=5,
        extra_payload={"custom": "value"}
    )
    assert hasattr(token, "token")
    assert token.type == "reset"

def test_register_rollback_on_error(db_session, mocker):
    user = User(
        firstname="Fail",
        lastname="User",
        email="fail@example.com",
        nickname="failuser",
        hashed_password="Password3",
        user_rol="user",
        phone="+1234567892"
    )
    mocker.patch.object(db_session, "commit", side_effect=Exception)
    with pytest.raises(Exception):
        auth_crud.register(db_session, user)