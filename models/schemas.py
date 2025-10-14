from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BasicInfo(BaseModel):
    title: Optional[str] = None
    event_id: Optional[str] = None
    date_of_release: Optional[str] = None
    date_of_submission: Optional[str] = None
    department_agency: Optional[str] = None
    type: Optional[str] = None
    objective: Optional[str] = None
    contract_term: Optional[str] = None
    total_budget: Optional[str] = None

class RiskFactor(BaseModel):
    score: int
    factors: List[str]
    mitigation: List[str]

class RiskAssessment(BaseModel):
    risk_factors: Dict[str, RiskFactor]
    overall_risk_score: float
    risk_level: str
    key_risks: List[str]

class CompatibilityAnalysis(BaseModel):
    overall_compatibility_score: int
    compatibility_level: str
    strengths_alignment: List[str]
    gaps_identified: List[str]
    recommendation: str
    risk_assessment: str
    key_differentiators: List[str]
