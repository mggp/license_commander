import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.services.classifier import ApplicationClassifier, ClassificationResult
from src.models import ApplicationType
from src.schemas import ApplicationDB
import pandas as pd
from unittest.mock import Mock, patch

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def classifier(db_session):
    return ApplicationClassifier(db_session)

def test_create_missing_applications_skips_existing(db_session, classifier):
    existing_app = ApplicationDB(id="1", name="Existing App", type=None)
    db_session.add(existing_app)
    db_session.commit()

    df = pd.DataFrame({
        'id': ['1', '2'],
        'name': ['Existing App', 'New App']
    })

    classifier.create_missing_applications_in_db(df)

    apps = db_session.query(ApplicationDB).all()
    assert len(apps) == 2
    assert any(app.name == "New App" for app in apps)

@patch('groq.Client')
def test_classify_application(mock_groq, classifier):
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Productividad|Herramienta de procesamiento de texto"
    mock_groq.return_value.chat.completions.create.return_value = mock_response

    result = classifier.classify_application("1", "Microsoft Word")

    assert isinstance(result, ClassificationResult)
    assert result.app_id == "1"
    assert result.type == "Productividad"

def test_update_applications_normalizes_type(db_session, classifier):
    app = ApplicationDB(id="1", name="Test App", type=None)
    db_session.add(app)
    db_session.commit()

    classification = ClassificationResult(
        app_id="1",
        type="Diseño",
        explanation="Herramienta de diseño gráfico"
    )

    classifier.update_applications_in_db({"1": classification})

    updated_app = db_session.query(ApplicationDB).filter(ApplicationDB.id == "1").first()
    assert updated_app.type == ApplicationType.DISENO 