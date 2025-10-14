# In utils/__init__.py - update to include the new functions
from .text_cleaning import clean_text, ensure_complete_sentences, fix_all_truncated_sentences

# Keep backward compatibility - alias the old function name
from .text_cleaning import ensure_complete_sentences as truncate_text