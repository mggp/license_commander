import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app
from src.models import ApplicationType
from src.schemas import ApplicationDB

# Configuración de la base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_applications():
    db = TestingSessionLocal()
    applications = [
        ApplicationDB(id="1", name="App 1", type=ApplicationType.PRODUCTIVIDAD),
        ApplicationDB(id="2", name="App 2", type=ApplicationType.DISENO),
        ApplicationDB(id="3", name="App 3", type=ApplicationType.COMUNICACION),
        ApplicationDB(id="4", name="App 4", type=ApplicationType.DESARROLLO),
        ApplicationDB(id="5", name="App 5", type=ApplicationType.FINANZAS),
    ]
    for app in applications:
        db.add(app)
    db.commit()
    db.close()
    return applications

def test_list_applications_default_page(sample_applications):
    response = client.get("/applications")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert len(data["items"]) == 5
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] == 1

def test_list_applications_pagination(sample_applications):
    response = client.get("/applications?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["pages"] == 3

def test_list_applications_second_page(sample_applications):
    response = client.get("/applications?page=2&size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2

def test_list_applications_last_page(sample_applications):
    response = client.get("/applications?page=3&size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["page"] == 3

def test_list_applications_invalid_page():
    response = client.get("/applications?page=0")
    assert response.status_code == 422

def test_list_applications_invalid_size():
    response = client.get("/applications?size=0")
    assert response.status_code == 422

def test_get_summary_empty():
    response = client.get("/applications/summary")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "productividad": 0,
        "diseno": 0,
        "comunicacion": 0,
        "desarrollo": 0,
        "finanzas": 0,
        "marketing": 0
    }

def test_get_summary_with_applications(sample_applications):
    response = client.get("/applications/summary")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "productividad": 1,
        "diseno": 1,
        "comunicacion": 1,
        "desarrollo": 1,
        "finanzas": 1,
        "marketing": 0
    }

def test_get_summary_with_multiple_applications():
    db = TestingSessionLocal()
    for i in range(3):
        app = ApplicationDB(id=i + 1, name=f"Productivity App {i}", type=ApplicationType.PRODUCTIVIDAD)
        db.add(app)
    db.commit()
    db.close()

    response = client.get("/applications/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["productividad"] == 3 