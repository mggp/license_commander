import pandas as pd
from typing import List, Dict, Tuple
import groq
from pathlib import Path
import os
from dotenv import load_dotenv
from src.models import ApplicationType
from src.schemas import ApplicationDB
from sqlalchemy.orm import Session
from dataclasses import dataclass

load_dotenv()

class ApplicationTypeMissing(Exception):
    def __init__(self, type_name: str):
        self.type_name = type_name
        super().__init__(f"El tipo de aplicación '{type_name}' no existe")

@dataclass
class ClassificationResult:
    app_id: str
    type: str
    explanation: str

class ApplicationClassifier:
    def __init__(self, db: Session):
        self.groq_client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))
        self.db = db
        self.system_prompt = """Eres un experto en clasificación de software empresarial. 
        Tu tarea es clasificar aplicaciones en una de estas categorías, no debes clasificar aplicaciones en más de una categoría ni en ninguna otra:
        - Productividad
        - Diseño
        - Comunicación
        - Desarrollo
        - Finanzas
        - Marketing
        
        Responde SÓLO con la categoría y una breve explicación (máximo 150 caracteres) separados por '|'.
        Ejemplo: 'Productividad|Herramienta de procesamiento de texto y hojas de cálculo'"""

    def read_applications_from_excel(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, names=['id', 'name'], skiprows=0)

    def create_missing_applications_in_db(self, applications: pd.DataFrame) -> None:
        for index, row in applications.iterrows():
            existing_app = self.db.query(ApplicationDB).filter(ApplicationDB.id == row['id']).first()
            if not existing_app:
                application = ApplicationDB(id=row['id'], name=row['name'], type=None)
                self.db.add(application)
        self.db.commit()

    def get_unclassified_applications(self) -> List[Dict]:
        return self.db.query(ApplicationDB).filter(ApplicationDB.type == None).all()

    def classify_application(self, application_id: str, application_name: str) -> ClassificationResult:
        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Clasifica esta aplicación: {application_name}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        category, explanation = response.choices[0].message.content.split('|')
        return ClassificationResult(
            app_id=application_id,
            type=category.strip(),
            explanation=explanation.strip()
        )

    def export_classifications(self, input_file: str, output_file: str, classifications: Dict[str, ClassificationResult], input_applications: pd.DataFrame) -> None:
        df = pd.read_excel(input_file, names=['id', 'name'])

        df['type'], df['explanation'] = zip(*df['id'].apply(lambda x: self.get_type_and_explanation(x, classifications)))
        df.to_excel(output_file, index=False)
    
    def get_type_and_explanation(self, app_id, new_classifications):
        if app_id in new_classifications:
            return new_classifications[app_id].type, new_classifications[app_id].explanation
        else:
            app = self.db.query(ApplicationDB).filter(ApplicationDB.id == app_id).first()
            if app and app.type:
                return app.type.name, "Aplicación clasificada con anterioridad"
            return None, None

    def update_applications_in_db(self, classifications: Dict[str, ClassificationResult]) -> None:
        for classification in classifications.values():
            try:
                app_type = ApplicationType(classification.type.lower())
            except KeyError:
                raise ApplicationTypeMissing(classification.type)

            self.db.query(ApplicationDB).filter(ApplicationDB.id == classification.app_id).update({
                'type': app_type,
            })
        self.db.commit()