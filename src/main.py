from fastapi import FastAPI, Depends, HTTPException
from services.classifier import ApplicationClassifier
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from math import ceil

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Application Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/applications", response_model=models.PaginatedResponse)
def list_applications(params: models.PaginationParams = Depends(), db: Session = Depends(get_db)):
    skip = (params.page - 1) * params.size
    total = db.query(schemas.ApplicationDB).count()
    applications = db.query(schemas.ApplicationDB).offset(skip).limit(params.size).all()
    pages = ceil(total / params.size)
    
    return {
        "items": applications,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": pages
    }

@app.get("/applications/type/{type}", response_model=models.PaginatedResponse)
def list_applications_by_type(
    type: models.ApplicationType,
    params: models.PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    skip = (params.page - 1) * params.size
    total = db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == type).count()
    applications = db.query(schemas.ApplicationDB).filter(schemas.ApplicationDB.type == type).offset(skip).limit(params.size).all()
    pages = ceil(total / params.size)
    
    return {
        "items": applications,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": pages
    }

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

@app.post("/applications/classify")
def classify_applications(db: Session = Depends(get_db), force_reclassify: bool = False):
    classifier = ApplicationClassifier(db)

    input_applications = classifier.read_applications_from_excel("input.xlsx")

    if force_reclassify:
        apps_to_classify = input_applications
    else:
        classifier.create_missing_applications_in_db(input_applications)
        apps_to_classify = classifier.get_unclassified_applications()

    classifications = {}
    for app in apps_to_classify:
        app_classification = classifier.classify_application(app.id, app.name)
        classifications[app_classification.app_id] = app_classification

    classifier.export_classifications("input.xlsx", "output.xlsx", classifications, input_applications)

    classifier.update_applications_in_db(classifications)

    return {"message": "Applications classified successfully"}