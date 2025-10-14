def ensure_complete_response(prompt: str, min_length: int = 50) -> str:
    """
    Enhance prompts to ensure complete responses from AI
    """
    completion_instructions = """

    IMPORTANT: Provide complete, well-formed sentences that end with proper punctuation.
    Do not truncate or cut off your response mid-sentence. Ensure every answer is a complete thought.
    If you need to be concise, still use complete sentences with proper endings.
    """

    return prompt + completion_instructions


def fix_truncated_ai_response(text: str, min_length: int = 10) -> str:
    """
    Fix common AI truncation patterns in responses
    """
    if not text or len(text) < min_length:
        return text or ""

    # Common truncation patterns to fix
    truncation_patterns = [
        # Fix incomplete sentences at the end
        (r'(\w+)\s*$', r'\1.'),  # Add period to last word
        (r'(\w+),\s*$', r'\1.'),  # Replace trailing comma with period
        (r'(\w+);\s*$', r'\1.'),  # Replace trailing semicolon with period
    ]

    fixed_text = text.strip()

    # Check if it ends with complete punctuation
    if fixed_text and fixed_text[-1] not in '.!?':
        # Try to find a reasonable place to add punctuation
        last_sentence_end = max(
            fixed_text.rfind('. '),
            fixed_text.rfind('! '),
            fixed_text.rfind('? ')
        )

        if last_sentence_end > len(fixed_text) * 0.7:
            # We have a recent sentence end, truncate there
            fixed_text = fixed_text[:last_sentence_end + 1]
        else:
            # Just add a period at the end
            fixed_text = fixed_text + '.'

    return fixed_text