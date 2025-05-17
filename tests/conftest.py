import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.db.session import engine
from app.models.address_model import Base as AddressBase
from app.models.user_model import Base as UserBase, User
from app.models.auth_model import Base as AuthBase

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
    user = User(id=1, username="testuser", email="test@example.com", hashed_password="1234")
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c