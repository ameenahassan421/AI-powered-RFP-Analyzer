import json
from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)


def extract_basic_information(text: str) -> dict:
    """Enhanced basic information extraction with anti-truncation measures"""

    prompt = """Extract comprehensive RFP information as JSON.

    CRITICAL INSTRUCTIONS:
    1. Provide COMPLETE values - never truncate words or cut off sentences
    2. Always use full, proper names and titles
    3. Ensure every field value is a complete thought
    4. If a value starts with a word that seems cut off, provide the full word

    Example of what NOT to do:
    - "oid Epidemic Response Services" → WRONG (truncated)
    - "Opioid Epidemic Response Services" → CORRECT (complete)

    Required JSON structure:
    {
        "title": "Complete, unabbreviated document title",
        "event_id": "Full RFP number or identifier", 
        "date_of_release": "Complete release date",
        "date_of_submission": "Full submission deadline",
        "department_agency": "Complete department/agency name",
        "type": "Complete document type",
        "objective": "Full objective statement",
        "contract_term": "Complete contract duration",
        "point_of_contact": "Full contact information",
        "total_budget": "Complete budget amount",
        "eligibility": "Full eligibility requirements",
        "evaluation_criteria": "Complete evaluation process",
        "scope_of_work": "Full scope description",
        "technical_requirements": "Complete technical specs",
        "submission_requirements": "Full submission details"
    }

    Remember: NEVER truncate words or cut off responses."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text[:6000]}],  # Reduced input
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=3500,  # Increased tokens for complete responses
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Apply post-processing
        from utils.text_cleaning import fix_ai_truncation_patterns, ensure_complete_sentences
        for key, value in result.items():
            if isinstance(value, str):
                result[key] = fix_ai_truncation_patterns(ensure_complete_sentences(value))

        return result

    except Exception as e:
        return {"error": f"Basic info extraction failed: {str(e)}"}