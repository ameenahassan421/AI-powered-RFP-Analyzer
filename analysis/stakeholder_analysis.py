def analyze_stakeholders(text: str) -> dict:
    """Stakeholder identification and analysis"""
    return {
        "decision_makers": [
            {"role": "Program Director", "influence": "High", "interest": "High", "key_concerns": ["Outcomes", "Budget"]},
            {"role": "Finance Officer", "influence": "Medium", "interest": "High", "key_concerns": ["Cost", "ROI"]},
            {"role": "Technical Lead", "influence": "Medium", "interest": "Medium", "key_concerns": ["Feasibility", "Innovation"]}
        ],
        "evaluation_committee": [
            "Technical Experts",
            "Community Representatives",
            "Subject Matter Experts"
        ],
        "key_contacts": [
            {"name": "RFP Coordinator", "role": "Primary Contact", "responsibilities": ["Clarifications", "Submission"]}
        ],
        "influence_map": {
            "high_power_high_interest": ["Program Director"],
            "high_power_low_interest": ["Finance Officer"],
            "low_power_high_interest": ["Community Representatives"],
            "low_power_low_interest": ["Administrative Staff"]
        }
    }
