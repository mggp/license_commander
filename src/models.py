from pydantic import BaseModel
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
    type: ApplicationType

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