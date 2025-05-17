import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user_model import Base as UserBase
from app.models.auth_model import Base as AuthBase
from app.models.address_model import Base as AddressBase
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    UserBase.metadata.create_all(bind=engine)
    AuthBase.metadata.create_all(bind=engine)
    AddressBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c