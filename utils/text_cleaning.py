import re

from utils.prompt_helpers import fix_truncated_ai_response


def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.{4,}', ' ', text)
    return text.strip()


def ensure_complete_sentences(text: str, max_length: int = None) -> str:
    """
    Ensure text ends with complete sentences
    If max_length provided, truncate but preserve sentence boundaries
    """
    if not text or not isinstance(text, str):
        return text or ""

    text = text.strip()
    if not text:
        return ""

    # If text already ends with sentence punctuation, return as is
    if text and text[-1] in '.!?':
        if max_length and len(text) > max_length:
            # Truncate but preserve the ending
            return text[:max_length - 1] + text[-1]
        return text

    # Find the last sentence boundary
    last_period = text.rfind('. ')
    last_excl = text.rfind('! ')
    last_quest = text.rfind('? ')

    last_boundary = max(last_period, last_excl, last_quest)

    if last_boundary > 0:
        # Return text up to the last complete sentence
        result = text[:last_boundary + 1]
        if max_length and len(result) > max_length:
            # If still too long, truncate more aggressively
            return ensure_complete_sentences(result, max_length)
        return result

    # No sentence boundaries found, return as is
    if max_length and len(text) > max_length:
        return text[:max_length]
    return text


def fix_ai_truncation_patterns(text: str) -> str:
    """
    Fix specific AI truncation patterns we're seeing
    - Words cut off at the beginning: 'oid' → 'Opioid', 'havioral' → 'Behavioral'
    - Words cut off at the beginning: 'ns' → 'modifications', 'monstrating' → 'demonstrating'
    - Incomplete phrases
    """
    if not text or not isinstance(text, str):
        return text or ""

    text = text.strip()
    if len(text) < 3:
        return text

    # Common truncation patterns we observed in your debug output
    truncation_fixes = {
        # Beginning truncations from your debug output
        r'^ns\b': 'Modifications',  # "ns allowed" → "Modifications allowed"
        r'^monstrating\b': 'Demonstrating',  # "monstrating cost-effectiveness" → "Demonstrating cost-effectiveness"

        # Government/agency terms
        r'^oid\b': 'Opioid',
        r'^havioral\b': 'Behavioral',
        r'^epartment\b': 'Department',
        r'^dministration\b': 'Administration',
        r'^ervices\b': 'Services',
        r'^equest\b': 'Request',
        r'^roposals\b': 'Proposals',
        r'^rantee\b': 'Grantee',
        r'^ovide\b': 'Provide',
        r'^pioid\b': 'Opioid',
        r'^pidemic\b': 'Epidemic',
        r'^esponse\b': 'Response',

        # Common incomplete words
        r'^hared\b': 'Shared',
        r'^osting\b': 'Hosting',
        r'^quirement\b': 'Requirement',
    }

    fixed_text = text

    # Apply pattern fixes
    for pattern, replacement in truncation_fixes.items():
        if re.search(pattern, fixed_text, re.IGNORECASE):
            fixed_text = re.sub(pattern, replacement, fixed_text, flags=re.IGNORECASE)

    # Fix specific phrases we're seeing
    phrase_fixes = {
        'ns allowed with prior approval': 'Modifications allowed with prior approval',
        'monstrating cost-effectiveness': 'Demonstrating cost-effectiveness',
        'option to extend for 1.5 years': 'Option to extend for 1.5 years',
        'No cost sharing required': 'No cost sharing required.',  # Add punctuation
        'Quarterly financial reports': 'Quarterly financial reports.',  # Add punctuation
    }

    # Check if the exact phrase matches
    if fixed_text in phrase_fixes:
        fixed_text = phrase_fixes[fixed_text]

    # Fix incomplete sentences at the end
    if fixed_text and fixed_text[-1] not in '.!?':
        # If it's a meaningful phrase (has spaces), add punctuation
        if ' ' in fixed_text and len(fixed_text) > 10:
            # Don't add punctuation if it's clearly a fragment that needs more context
            if not any(fragment in fixed_text.lower() for fragment in ['allowed with', 'required', 'reports']):
                fixed_text = fixed_text + '.'

    return fixed_text


# In fix_ai_truncation_patterns, remove specific RFP content:
def fix_ai_truncation_patterns(text: str) -> str:
    """
    Fix common AI truncation patterns (GENERALIZED)
    """
    if not text or not isinstance(text, str):
        return text or ""

    text = text.strip()
    if len(text) < 3:
        return text

    # ONLY keep generalized patterns
    generalized_fixes = {
        r'^[a-z]': lambda m: m.group().upper(),  # Capitalize first letter
        r'^\d+-': 'RFP-',  # Add RFP prefix to numbers with dash
        r'^\d': '$',  # Add dollar sign to numbers (financial)
    }

    fixed_text = text

    # Apply generalized fixes
    for pattern, replacement in generalized_fixes.items():
        if isinstance(replacement, str):
            if re.match(pattern, fixed_text):
                fixed_text = re.sub(pattern, replacement, fixed_text)
        else:  # Function
            match = re.match(pattern, fixed_text)
            if match:
                fixed_text = replacement(match) + fixed_text[1:]

    return fixed_text


def complete_financial_sentences(text: str, field_name: str = "") -> str:
    """
    Complete financial-related sentences based on common patterns we're seeing
    """
    if not text:
        return text

    # Common financial sentence beginnings and their completions from your debug output
    financial_completions = {
        # From your debug output:
        'y and annual': 'Quarterly and annual',
        'al audit': 'Annual audit',
        'the budget': 'Modify the budget',
        'e for the': 'Funding is available for the',
        'ns allowed': 'Modifications allowed',
        'monstrating': 'Demonstrating',

        # Previous patterns:
        'oid ': 'Opioid ',
        'havioral ': 'Behavioral ',
    }

    # Check if text starts with any known truncation pattern
    for truncated, complete in financial_completions.items():
        if text.startswith(truncated):
            completed_text = complete + text[len(truncated):]
            # Ensure it ends with proper punctuation
            if completed_text and completed_text[-1] not in '.!?':
                completed_text = completed_text + '.'
            return completed_text

    # Field-specific completions for more precise fixes
    field_completions = {
        'financial_reporting': {
            'y and annual': 'Quarterly and annual',
            'al audit': 'Annual audit',
        },
        'audit_requirements': {
            'al audit': 'Annual audit',
        },
        'budget_flexibility': {
            'the budget': 'Modify the budget',
            'ns allowed': 'Modifications allowed',
        },
        'funding_stability': {
            'e for the': 'Funding is available for the',
        },
        'winning_strategy': {
            'monstrating': 'Demonstrating',
        }
    }

    # Apply field-specific completions
    if field_name in field_completions:
        for truncated, complete in field_completions[field_name].items():
            if text.startswith(truncated):
                completed_text = complete + text[len(truncated):]
                # Ensure it ends with proper punctuation
                if completed_text and completed_text[-1] not in '.!?':
                    completed_text = completed_text + '.'
                return completed_text

    return text


def fix_all_truncated_sentences(results):
    """Apply aggressive AI truncation fixing to all results with context awareness"""
    if not isinstance(results, dict):
        return results

    fixed_results = {}

    for category, data in results.items():
        if isinstance(data, dict):
            fixed_results[category] = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Step 1: Context-aware completion for financial fields
                    step1 = complete_financial_sentences(value, key)

                    # Step 2: Pattern-based fixes
                    step2 = fix_ai_truncation_patterns(step1)

                    # Step 3: Sentence completion
                    step3 = ensure_complete_sentences(step2)

                    # Step 4: Final cleanup
                    step4 = fix_truncated_ai_response(step3)

                    fixed_results[category][key] = step4

                elif isinstance(value, list):
                    fixed_results[category][key] = [
                        complete_financial_sentences(
                            fix_ai_truncation_patterns(
                                ensure_complete_sentences(
                                    fix_truncated_ai_response(str(item))
                                )
                            ), key
                        ) if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    fixed_results[category][key] = value
        else:
            if isinstance(data, str):
                fixed_results[category] = complete_financial_sentences(
                    fix_ai_truncation_patterns(
                        ensure_complete_sentences(
                            fix_truncated_ai_response(data)
                        )
                    )
                )
            else:
                fixed_results[category] = data

    return fixed_results

def complete_financial_sentences(text: str, field_name: str = "") -> str:
    """
    Complete financial-related sentences based on common patterns
    """
    if not text:
        return text

    # Common financial sentence beginnings and their completions
    financial_completions = {
        'y and annual': 'Quarterly and annual',
        'al audit': 'Annual audit',
        'the budget': 'Modify the budget',
        'e for the': 'Funding is available for the',
        'ns allowed': 'Modifications allowed',
    }

    # Check if text starts with any known truncation pattern
    for truncated, complete in financial_completions.items():
        if text.startswith(truncated):
            return complete + text[len(truncated):]

    # Field-specific completions
    field_completions = {
        'financial_reporting': {
            'y and annual': 'Quarterly and annual',
            'al audit': 'Annual audit',
        },
        'budget_flexibility': {
            'the budget': 'Modify the budget',
            'ns allowed': 'Modifications allowed',
        },
        'funding_stability': {
            'e for the': 'Funding is available for the',
        }
    }

    # Apply field-specific completions
    if field_name in field_completions:
        for truncated, complete in field_completions[field_name].items():
            if text.startswith(truncated):
                return complete + text[len(truncated):]

    return text
# Backward compatibility - alias the old function name
def truncate_text(text: str, max_length: int) -> str:
    """Backward compatibility alias for ensure_complete_sentences"""
    return ensure_complete_sentences(text, max_length)