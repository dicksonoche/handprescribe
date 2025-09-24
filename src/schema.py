from pydantic import BaseModel, field_validator

class PrescriptionSchema(BaseModel):
    drug_name: str
    dosage: str
    route: str
    frequency: str
    duration: str
    confidence: float

    @field_validator('route')
    @classmethod
    def normalize_route(cls, v: str) -> str:
        abbr = {"po": "oral", "p.o.": "oral"}
        return abbr.get(v.lower(), v)
    # For adding more validators