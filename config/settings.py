import os

# API Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
MODEL_NAME = "llama-3.1-8b-instant"

# File Processing Settings
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]

# Analysis Settings
MAX_TEXT_LENGTH = 6000
TEMPERATURE = 0.1
MAX_TOKENS = 10000

# UI Settings
PAGE_TITLE = "RFP Intelligence Pro"
PAGE_ICON = "🚀"
LAYOUT = "wide"
