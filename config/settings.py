import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env locally (harmless if not present on Streamlit Cloud)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def get_secret(name: str) -> str:
    """Retrieve secret from Streamlit Cloud or .env"""
    # 1️⃣ Streamlit Cloud secrets
    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    # 2️⃣ Environment variable / .env (local)
    value = os.getenv(name)
    if value:
        return value

    # 3️⃣ Fail clearly if missing
    raise RuntimeError(f"Missing required secret: {name}")

# --- API Configuration ---
GROQ_API_KEY = get_secret("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

# --- File Processing Settings ---
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]

# --- Analysis Settings ---
MAX_TEXT_LENGTH = 6000
TEMPERATURE = 0.1
MAX_TOKENS = 10000

# --- UI Settings ---
PAGE_TITLE = "RFP Intelligence Pro"
PAGE_ICON = "🚀"
LAYOUT = "wide"
