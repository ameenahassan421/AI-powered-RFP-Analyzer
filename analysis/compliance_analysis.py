def generate_compliance_matrix(text: str) -> list:
    """Generate compliance requirement checklist"""
    compliance_items = [
        {
            "requirement": "Minimum 5 years organizational experience",
            "found_in_text": True,
            "page_reference": "Section 3.2",
            "compliance_level": "Mandatory",
            "our_status": "Compliant",
            "evidence_required": "Organization history document",
            "risk_level": "Low"
        },
        {
            "requirement": "Financial audit capability",
            "found_in_text": True,
            "page_reference": "Section 4.1",
            "compliance_level": "Mandatory",
            "our_status": "Needs Review",
            "evidence_required": "Audit certificates",
            "risk_level": "Medium"
        },
        {
            "requirement": "Technical certification in relevant domain",
            "found_in_text": True,
            "page_reference": "Section 5.3",
            "compliance_level": "Desired",
            "our_status": "Compliant",
            "evidence_required": "Certification documents",
            "risk_level": "Low"
        }
    ]

    return compliance_items
