from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Application Classification API")

@app.get("/applications", response_model=List[models.Application])
def list_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    applications = db.query(schemas.ApplicationDB).offset(skip).limit(limit).all()
    return applications

@app.get("/applications/summary", response_model=models.CategorySummary)
def get_summary(db: Session = Depends(get_db)):
    summary = {
        "productividad": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.PRODUCTIVIDAD).count(),
        "diseno": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.DISENO).count(),
        "comunicacion": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.COMUNICACION).count(),
        "desarrollo": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.DESARROLLO).count(),
        "finanzas": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.FINANZAS).count(),
        "marketing": db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == models.ApplicationType.MARKETING).count()
    }
    return summary

@app.put("/applications/{application_id}", response_model=models.Application)
def update_application(application_id: int, application: models.ApplicationUpdate, db: Session = Depends(get_db)):
    db_application = db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.id == application_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    for key, value in application.dict().items():
        setattr(db_application, key, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application 