import json
from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME, TEMPERATURE

client = Groq(api_key=GROQ_API_KEY)

def analyze_financials(text: str) -> dict:
    """Deep financial analysis"""
    prompt = """Analyze financial aspects and return detailed JSON:
    {
        "total_budget": "Total contract value with currency",
        "annual_budget": "Yearly funding breakdown",
        "payment_schedule": "Payment terms and milestones",
        "cost_sharing": "Cost sharing or matching requirements",
        "allowable_costs": "What costs are allowable vs unallowable",
        "budget_categories": "Budget breakdown by categories",
        "indirect_cost_rate": "Indirect cost rate policy",
        "financial_reporting": "Financial reporting requirements",
        "audit_requirements": "Audit and compliance requirements",
        "budget_flexibility": "Budget modification possibilities",
        "funding_stability": "Funding source and stability assessment"
    }"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text[:10000]}],
            temperature=TEMPERATURE,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        financial_data = json.loads(response.choices[0].message.content)

        # Add calculated metrics
        if financial_data.get('total_budget'):
            financial_data['financial_score'] = calculate_financial_score(financial_data)

        return financial_data
    except Exception as e:
        return {"error": f"Financial analysis failed: {str(e)}"}

def calculate_financial_score(financial_data: dict) -> int:
    """Calculate financial health score (0-100)"""
    score = 70  # Base score

    if financial_data.get('total_budget'):
        score += 10
    if financial_data.get('payment_schedule'):
        score += 5
    if financial_data.get('budget_categories'):
        score += 10
    if financial_data.get('funding_stability'):
        if 'stable' in str(financial_data.get('funding_stability', '')).lower():
            score += 5

    return min(100, score)
