# models.py
from pydantic import BaseModel, Field
from typing import Dict, Optional

class SubmissionModel(BaseModel):
    age: Optional[int] = Field(None, ge=0)
    gender: Optional[str] = Field(None)
    symptoms: Dict[str, Optional[str]]  # keys to values e.g. "fever": "high" or bools
    tests: Optional[Dict[str, Optional[str]]] = None
    consent_store: Optional[bool] = False
