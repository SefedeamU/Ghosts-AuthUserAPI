import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import hash_password
from app.main import app
from app.db.session import engine
from app.models.address_model import Base as AddressBase
from app.models.user_model import Base as UserBase, User
from app.models.auth_model import Base as AuthBase

# Mock más específico para email - interceptar en múltiples puntos
@pytest.fixture(autouse=True)
def mock_email_sending():
    """Mock email sending for all tests automatically"""
    patches = [
        patch('app.utils.email_utils.send_email'),
        patch('app.api.auth_routes.send_email'),  # Si se importa directamente en auth_routes
        patch('smtplib.SMTP'),  # Mock directo de SMTP
    ]
    
    mocks = []
    for patch_obj in patches:
        try:
            mock = patch_obj.start()
            mock.return_value = None
            mocks.append(mock)
        except:
            # Si algún patch falla, continúa con los otros
            pass
    
    yield mocks
    
    # Cleanup
    for patch_obj in patches:
        try:
            patch_obj.stop()
        except:
            pass

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    UserBase.metadata.create_all(bind=engine)
    AuthBase.metadata.create_all(bind=engine)
    AddressBase.metadata.create_all(bind=engine)
    yield
    AddressBase.metadata.drop_all(bind=engine)
    AuthBase.metadata.drop_all(bind=engine)
    UserBase.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def clean_tables():
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    db.execute(text("DELETE FROM addresses"))
    db.execute(text("DELETE FROM action_tokens"))
    db.execute(text("DELETE FROM password_restore_tokens"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    db.close()

@pytest.fixture(scope="function")
def db_session():
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        id=1,
        firstname="Test",
        lastname="User",
        email="test@example.com",
        nickname="testuser",
        hashed_password=hash_password("Password1"),
        user_rol="user",
        phone="+1234567890"
    )
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture(scope="function")
def client():
    return TestClient(app)