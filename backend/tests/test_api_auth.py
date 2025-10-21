"""
Tests for Authentication API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.models import Base, User
from app.db.session import get_db
from app.utils.security import hash_password


# Create in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    
    # Create test user
    db = TestingSessionLocal()
    import time
    test_user = User(
        username="testuser",
        password_hash=hash_password("testpass123"),
        role="operator",
        is_active=True,
        created_at=int(time.time())
    )
    db.add(test_user)
    db.commit()
    db.close()
    
    yield TestClient(app)
    
    Base.metadata.drop_all(bind=engine)


def test_login_success(client):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["role"] == "operator"


def test_login_invalid_username(client):
    """Test login with invalid username"""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "testpass123"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_invalid_password(client):
    """Test login with invalid password"""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_inactive_user(client):
    """Test login with inactive user"""
    # Create inactive user
    import time
    db = TestingSessionLocal()
    inactive_user = User(
        username="inactive",
        password_hash=hash_password("testpass"),
        role="viewer",
        is_active=False,
        created_at=int(time.time())
    )
    db.add(inactive_user)
    db.commit()
    db.close()
    
    response = client.post(
        "/api/auth/login",
        json={"username": "inactive", "password": "testpass"}
    )
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()
