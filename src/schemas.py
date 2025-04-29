from sqlalchemy import Column, Integer, String, Enum
from .database import Base
from .models import ApplicationType

class ApplicationDB(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum(ApplicationType))

