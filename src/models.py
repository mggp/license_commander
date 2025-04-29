from pydantic import BaseModel
from typing import Optional
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
    version: str
    type: ApplicationType

class ApplicationUpdate(BaseModel):
    type: ApplicationType

class CategorySummary(BaseModel):
    productividad: int
    diseno: int
    comunicacion: int
    desarrollo: int
    finanzas: int
    marketing: int 