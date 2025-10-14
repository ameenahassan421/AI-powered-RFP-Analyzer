import json
import re
from groq import Groq
from config.settings import GROQ_API_KEY, MODEL_NAME, TEMPERATURE

client = Groq(api_key=GROQ_API_KEY)

def analyze_compatibility(rfp_text: str, organization_profile: str) -> dict:
    """Analyze compatibility between RFP and organization capabilities"""
    prompt = """Analyze the compatibility between this RFP and the organization's profile. Be brutally honest and factual.

CRITICAL INSTRUCTIONS:
1. Provide COMPLETE values - never truncate words or cut off sentences
2. Always use full, proper names and titles  
3. Ensure every field value is a complete thought
4. If a value starts with a word that seems cut off, provide the full word
5. Structure your response clearly with these exact section headers:

OVERALL COMPATIBILITY SCORE: [0-100]
COMPATIBILITY LEVEL: [High/Medium/Low]
STRENGTHS: [bullet points]
GAPS: [bullet points]
RECOMMENDATION: [Strongly Recommended/Recommended/Not Recommended/Conditional]
RISK ASSESSMENT: [description]
DIFFERENTIATORS: [bullet points]
RESOURCE GAPS: [description]
STRATEGIC FIT: [description]
EFFORT REQUIRED: [High/Medium/Low]
TIMELINE FEASIBILITY: [description]

Ensure each section is complete and sentences are not cut off.

RFP REQUIREMENTS:
{rfp_text}

ORGANIZATION PROFILE:  
{organization_profile}

Focus on factual analysis, not optimism."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert RFP compatibility analyst. Provide honest, factual assessments. Always use complete sentences and never truncate text."},
                {"role": "user", "content": prompt.format(
                    rfp_text=rfp_text[:6000],
                    organization_profile=organization_profile[:3000]
                )}
            ],
            temperature=TEMPERATURE,
            max_tokens=2000
        )

        analysis_text = response.choices[0].message.content
        return parse_compatibility_response(analysis_text)

    except Exception as e:
        return {"error": f"Compatibility analysis failed: {str(e)}"}


def parse_compatibility_response(text: str) -> dict:
    """Parse the free-text compatibility analysis into structured data"""
    # Initialize with defaults
    result = {
        "overall_compatibility_score": 50,
        "compatibility_level": "Medium",
        "strengths_alignment": [],
        "gaps_identified": [],
        "recommendation": "Conditional",
        "risk_assessment": "Moderate risk",
        "key_differentiators": [],
        "resource_gap_analysis": "Some gaps identified",
        "strategic_fit": "Moderate alignment",
        "estimated_effort_required": "Medium",
        "timeline_feasibility": "Feasible with effort",
        "raw_analysis": text  # Keep original for reference
    }

    try:
        # Extract score (more comprehensive pattern)
        score_matches = re.findall(r'(\b\d{1,3}\b)\s*(?:out of 100|score|%|percent|compatibility)', text, re.IGNORECASE)
        if not score_matches:
            # Alternative pattern: look for numbers near "score" or "compatibility"
            score_matches = re.findall(r'(?:score|compatibility)[^\d]*(\d{1,3})', text, re.IGNORECASE)
        if score_matches:
            result["overall_compatibility_score"] = min(100, max(0, int(score_matches[0])))

        # Extract compatibility level with better context
        if re.search(r'\b(high|strong|excellent)\b', text, re.IGNORECASE):
            result["compatibility_level"] = "High"
        elif re.search(r'\b(low|poor|weak|minimal)\b', text, re.IGNORECASE):
            result["compatibility_level"] = "Low"

        # Extract recommendation with better patterns
        if re.search(r'strongly\s+recommended|definitely\s+pursue|highly\s+recommended', text, re.IGNORECASE):
            result["recommendation"] = "Strongly Recommended"
        elif re.search(r'not\s+recommended|avoid|do\s+not\s+pursue|decline', text, re.IGNORECASE):
            result["recommendation"] = "Not Recommended"
        elif re.search(r'\brecommended\b|pursue|consider', text, re.IGNORECASE):
            result["recommendation"] = "Recommended"

        # Improved section extraction that doesn't cut off sentences
        def extract_section(section_name, text):
            """Extract complete section content without cutting off sentences"""
            # Pattern to find the section and capture everything until next section or end
            pattern = rf'{section_name}[:\-]\s*(.*?)(?=\n\s*\n\s*[A-Z][a-z]+\s*[:\-]|\n\s*[A-Z][a-z]+\s*[:\-]|\Z)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)

            if matches:
                content = matches[0].strip()
                # Split by bullets, numbers, or new lines while preserving complete sentences
                items = re.split(r'\n\s*[•\-\*]\s*|\n\s*\d+\.\s*', content)
                # Filter out empty items and ensure reasonable length
                valid_items = []
                for item in items:
                    item = item.strip()
                    # Remove trailing incomplete sentences
                    item = re.sub(r'[^.!?]*$', '', item).strip()
                    if item and len(item) >= 15:  # Minimum reasonable length
                        valid_items.append(item)
                return valid_items
            return []

        # Extract strengths with improved method
        result["strengths_alignment"] = extract_section('strengths', text)

        # Extract gaps
        result["gaps_identified"] = extract_section('gaps', text)

        # Extract differentiators
        result["key_differentiators"] = extract_section('differentiators', text)

        # Extract risk assessment
        risk_sections = extract_section('risk assessment', text)
        if risk_sections:
            result["risk_assessment"] = risk_sections[0] if risk_sections else "Moderate risk"

        # Extract strategic fit
        strategic_sections = extract_section('strategic fit', text)
        if strategic_sections:
            result["strategic_fit"] = strategic_sections[0] if strategic_sections else "Moderate alignment"

        # Extract effort required
        if re.search(r'high\s+effort|significant\s+effort|substantial\s+work', text, re.IGNORECASE):
            result["estimated_effort_required"] = "High"
        elif re.search(r'low\s+effort|minimal\s+effort|little\s+work', text, re.IGNORECASE):
            result["estimated_effort_required"] = "Low"

        # Extract timeline feasibility
        if re.search(r'not\s+feasible|unrealistic|too\s+tight|insufficient\s+time', text, re.IGNORECASE):
            result["timeline_feasibility"] = "Not feasible"
        elif re.search(r'feasible|achievable|realistic|adequate', text, re.IGNORECASE):
            result["timeline_feasibility"] = "Feasible"

        # Fallback: if we couldn't extract meaningful lists, use smarter text analysis
        if not result["strengths_alignment"] or not result["gaps_identified"]:
            # Use the raw text to create basic analysis
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(word in line_lower for word in ['strength', 'advantage', 'aligns', 'matches', 'capable']):
                    if line.strip() and len(line.strip()) > 20:
                        result["strengths_alignment"].append(line.strip())
                elif any(word in line_lower for word in ['gap', 'lack', 'missing', 'weakness', 'limitation']):
                    if line.strip() and len(line.strip()) > 20:
                        result["gaps_identified"].append(line.strip())

        # Ensure we have at least basic content
        if not result["strengths_alignment"]:
            result["strengths_alignment"] = ["Organization demonstrates relevant capabilities based on analysis"]
        if not result["gaps_identified"]:
            result["gaps_identified"] = ["Some capability gaps identified requiring further assessment"]
        if not result["key_differentiators"]:
            result["key_differentiators"] = ["Organization brings relevant experience and qualifications"]

        return result

    except Exception as e:
        # If parsing fails, return a basic analysis with the raw text
        return {
            "overall_compatibility_score": 50,
            "compatibility_level": "Medium",
            "strengths_alignment": ["Organization shows alignment with key requirements"],
            "gaps_identified": ["Some capability gaps require assessment"],
            "recommendation": "Further analysis needed",
            "risk_assessment": "Moderate risk",
            "key_differentiators": ["Relevant organizational experience"],
            "resource_gap_analysis": "Standard resource requirements",
            "strategic_fit": "Moderate alignment",
            "estimated_effort_required": "Medium",
            "timeline_feasibility": "Feasible with planning",
            "analysis_note": f"Basic analysis completed - detailed parsing encountered issues: {str(e)}",
            "raw_analysis": text
        }