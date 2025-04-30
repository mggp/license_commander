from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ApplicationType(str, Enum):
    PRODUCTIVIDAD = "productividad"
    DISENO = "diseno"
    COMUNICACION = "comunicacion"
    DESARROLLO = "desarrollo"
    FINANZAS = "finanzas"
    MARKETING = "marketing"

class Application(BaseModel):
    id: int
    name: str
    type: ApplicationType | None = None

class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ApplicationType] = None

class PaginationParams(BaseModel):
    page: int = Field(ge=1, default=1)
    size: int = Field(ge=1, default=10)

class CategorySummary(BaseModel):
    productividad: int
    diseno: int
    comunicacion: int
    desarrollo: int
    finanzas: int
    marketing: int

class PaginatedResponse(BaseModel):
    items: List[Application]
    total: int
    page: int
    size: int
    pages: int 