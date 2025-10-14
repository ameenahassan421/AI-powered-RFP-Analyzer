from .basic_analysis import extract_basic_information
from .financial_analysis import analyze_financials, calculate_financial_score
from .risk_analysis import assess_risks
from .competitive_analysis import analyze_competitiveness
from .compatibility_analysis import analyze_compatibility
from .compliance_analysis import generate_compliance_matrix
from .stakeholder_analysis import analyze_stakeholders
from .content_generation import generate_proposal_content

def multi_stage_rfp_analysis(text: str, organization_profile: str = None) -> dict:
    """Comprehensive multi-stage RFP analysis"""
    analysis_results = {}

    # Stage 1: Basic Information Extraction
    analysis_results['basic_info'] = extract_basic_information(text)

    # Stage 2: Financial Deep Dive
    analysis_results['financial_analysis'] = analyze_financials(text)

    # Stage 3: Risk Assessment
    analysis_results['risk_assessment'] = assess_risks(text, analysis_results['basic_info'])

    # Stage 4: Competitive Intelligence
    analysis_results['competitive_analysis'] = analyze_competitiveness(text, analysis_results['basic_info'])

    # Stage 5: Resource & Timeline Planning
    analysis_results['resource_planning'] = plan_resources_timeline(analysis_results['basic_info'])

    # Stage 6: Compliance Matrix
    analysis_results['compliance_matrix'] = generate_compliance_matrix(text)

    # Stage 7: Stakeholder Analysis
    analysis_results['stakeholder_analysis'] = analyze_stakeholders(text)

    # Stage 8: Content Generation
    analysis_results['content_suggestions'] = generate_proposal_content(analysis_results)

    # Stage 9: Compatibility Analysis
    if organization_profile:
        analysis_results['compatibility_analysis'] = analyze_compatibility(text, organization_profile)

    return analysis_results

def plan_resources_timeline(basic_info: dict) -> dict:
    """Resource planning and timeline analysis - moved here to avoid circular imports"""
    from datetime import datetime, timedelta

    # Calculate timeline from submission date
    submission_date = basic_info.get('date_of_submission', '2025-01-01')
    try:
        submit_dt = datetime.strptime(submission_date, '%B %d, %Y')
    except:
        submit_dt = datetime(2025, 1, 1)

    milestones = [
        {"task": "Initial Review & Analysis", "days": 2, "team": ["PM", "Analyst"]},
        {"task": "Solution Design & Strategy", "days": 5, "team": ["Tech Lead", "Architect"]},
        {"task": "Proposal Writing", "days": 7, "team": ["Writer", "Subject Experts"]},
        {"task": "Financial Modeling", "days": 3, "team": ["Finance", "Pricing"]},
        {"task": "Review & Quality Assurance", "days": 3, "team": ["PM", "Legal", "Quality"]},
        {"task": "Final Submission", "days": 1, "team": ["PM"]}
    ]

    current_date = submit_dt
    timeline = []
    for milestone in reversed(milestones):
        start_date = current_date - timedelta(days=milestone['days'])
        timeline.append({
            **milestone,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": current_date.strftime('%Y-%m-%d')
        })
        current_date = start_date

    timeline.reverse()

    return {
        "total_estimated_hours": 160,
        "team_requirements": ["Project Manager", "Technical Lead", "Finance Analyst", "Subject Expert", "Writer"],
        "timeline_milestones": timeline,
        "critical_path": ["Solution Design & Strategy", "Proposal Writing"],
        "resource_constraints": ["Subject matter expertise", "Review capacity"],
        "recommended_start_date": timeline[0]['start_date'] if timeline else None
    }
