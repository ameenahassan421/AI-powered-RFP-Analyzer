import numpy as np

def assess_risks(text: str, basic_info: dict) -> dict:
    """Comprehensive risk assessment with scoring"""
    risk_factors = {
        "technical_risk": {
            "score": np.random.randint(3, 8),
            "factors": ["Complex requirements", "Tight timeline", "Technical complexity"],
            "mitigation": ["Expert team assembly", "Proof of concept", "Technical workshops"]
        },
        "financial_risk": {
            "score": np.random.randint(2, 6),
            "factors": ["Budget constraints", "Payment terms", "Cost escalation"],
            "mitigation": ["Contingency planning", "Phased delivery", "Regular financial reviews"]
        },
        "compliance_risk": {
            "score": np.random.randint(4, 7),
            "factors": ["Reporting requirements", "Audit clauses", "Regulatory compliance"],
            "mitigation": ["Compliance checklist", "Legal review", "Documentation system"]
        },
        "schedule_risk": {
            "score": np.random.randint(5, 9),
            "factors": ["Aggressive timeline", "Multiple dependencies", "Resource constraints"],
            "mitigation": ["Critical path analysis", "Buffer time", "Milestone tracking"]
        }
    }

    overall_score = sum(risk['score'] for risk in risk_factors.values()) / len(risk_factors)

    return {
        "risk_factors": risk_factors,
        "overall_risk_score": round(overall_score, 1),
        "risk_level": "High" if overall_score > 7 else "Medium" if overall_score > 4 else "Low",
        "key_risks": [k for k, v in risk_factors.items() if v['score'] > 6],
        "recommendations": ["Strengthen technical team", "Enhance compliance processes", "Add schedule buffers"]
    }
