# ui/dashboard.py
import base64
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

import streamlit as st

# Local imports
from utils.file_processing import process_uploaded_file
from utils.text_cleaning import clean_text
from analysis import multi_stage_rfp_analysis
from .tabs import display_all_tabs


# ---------- Configuration ----------
@dataclass
class AppConfig:
    SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]
    MAX_FILE_SIZE_MB = 50
    ANALYSIS_TIMEOUT = 300
    MIN_TEXT_LENGTH = 50

    # Enhanced configuration with environment variables
    DEBUG: bool = False
    MAX_FILE_SIZE: int = 50
    API_TIMEOUT: int = 300

    def __post_init__(self):
        self.DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        self.API_TIMEOUT = int(os.getenv('API_TIMEOUT', '300'))


# ---------- helpers ----------
def _load_logo_b64() -> Optional[str]:
    """
    Try common locations for the Atharii logo with better error reporting.
    """
    candidates = [
        Path(__file__).parent / "logo_Athari.png",  # ui/logo_Athari.png
        Path("ui/logo_Athari.png"),
        Path("logo_Athari.png"),  # Fixed typo
        Path("assets/logo_Athari.png"),
        Path("/mnt/data/logo_Athari.png"),
    ]

    for path in candidates:
        if path.exists():
            try:
                return base64.b64encode(path.read_bytes()).decode()
            except Exception as e:
                print(f"Error loading logo from {path}: {e}")
                continue

    st.sidebar.warning("Logo image not found. Using text header.")
    return None


def _validate_file_upload(uploaded_file) -> bool:
    """Validate uploaded file size and type."""
    if uploaded_file is None:
        return True

    # Check file type
    file_extension = Path(uploaded_file.name).suffix.lower()[1:]
    if file_extension not in AppConfig.SUPPORTED_FILE_TYPES:
        st.error(
            f"Unsupported file type: .{file_extension}. Supported types: {', '.join(AppConfig.SUPPORTED_FILE_TYPES)}")
        return False

    # Check file size
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
    if file_size > AppConfig.MAX_FILE_SIZE_MB:
        st.error(f"File too large: {file_size:.1f}MB. Maximum size is {AppConfig.MAX_FILE_SIZE_MB}MB")
        return False

    return True


def _inject_css():
    st.markdown("""
    <style>
      :root{
        --ath-bg:        #F7F1E6;
        --ath-surface:   #FFFFFF;
        --ath-border:    #E6E0D3;
        --ath-text:      #1E2328;
        --ath-muted:     #5F676F;
        --ath-olive:     #6F7B57;
        --ath-olive-dark:#555F40;
        --ath-amber:     #D7A13C;
        --ath-terr:      #CB5B3D;
      }

      /* Global styles - DARK TEXT EVERYWHERE */
      html, body, .stApp, [data-testid="stAppViewContainer"]{ 
        background: var(--ath-bg) !important; 
        color: var(--ath-olive-dark) !important; 
      }

      /* Force ALL text to be dark */
      * {
        color: var(--ath-olive-dark) !important;
      }

      .block-container{ max-width: 1120px !important; padding-top: 1.25rem !important; }

      /* Hero */
      .main-header{ 
        background: linear-gradient(180deg,#FFFDF8 0%, #F7F1E6 100%);
        border:1px solid var(--ath-border); border-radius:16px;
        padding:24px 28px; margin:16px auto 18px; box-shadow:0 6px 20px rgba(0,0,0,.04); 
      }
      .hero-center{ display:flex; flex-direction:column; align-items:center; text-align:center; gap:10px; }
      .hero-logo{ height:64px; width:auto; display:block; }
      .hero-title{ margin:0; line-height:1.15; font-weight:900; color: var(--ath-olive-dark); }
      .hero-sub{ margin:6px 0 0; color: var(--ath-olive); }
      .hero-chips{ display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-top:8px; }
      .hero-chip{ background:#fff; border:1px solid var(--ath-border); border-radius:999px; padding:4px 10px; font-size:.85rem; color: var(--ath-olive); }

      /* Section wrapper */
      .section-card{ background: var(--ath-surface); border:1px solid var(--ath-border); border-radius:14px; padding:12px 16px; margin-top:10px; }

      /* Upload tiles */
      .upload-tile{ background: var(--ath-surface); border:1px solid var(--ath-border); border-radius:12px; padding:12px; }

      /* OR divider + textarea */
      .stTextArea textarea{ 
        background:#FFFFFF !important; 
        border:1px solid var(--ath-border) !important; 
        color: var(--ath-olive-dark) !important; 
        border-radius:10px !important; 
        min-height:140px !important; 
      }
      .or-divider{ position:relative; text-align:center; margin:10px 0 12px; }
      .or-divider:before{ content:""; display:block; height:1px; background:var(--ath-border); position:absolute; left:0; right:0; top:50%; }
      .or-divider span{ 
        position:relative; padding:2px 10px; background:#FFF; border:1px solid var(--ath-border); 
        border-radius:999px; color: var(--ath-muted) !important; font-size:.85rem; 
      }

      /* Tabs */
      div[data-baseweb="tab-list"], [role="tablist"]{
        position: sticky; top: 0; z-index: 70; background: var(--ath-bg);
        border-bottom:3px solid var(--ath-olive); padding:10px 8px; margin:8px 0 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,.06);
      }
      div[data-baseweb="tab"], [role="tab"]{
        font-weight:700; font-size:.98rem; color: var(--ath-olive) !important; background:#fff;
        border:1px solid var(--ath-border); border-radius:12px; padding:8px 12px; margin-right:6px;
      }
      div[data-baseweb="tab"]:hover, [role="tab"]:hover{ border-color: var(--ath-amber); }
      div[data-baseweb="tab-highlight"]{ background: var(--ath-terr) !important; height:3px; }
      [role="tab"][aria-selected="true"]{ background: linear-gradient(180deg,#FFF,#FFF8EC); color: var(--ath-olive-dark) !important; border-color: var(--ath-amber); }

      /* Atharii banner */
      .ath-banner{ 
        background:#FFFDF6; border:1px solid var(--ath-border); border-left:6px solid var(--ath-olive);
        border-radius:12px; display:flex; align-items:center; gap:10px; padding:10px 12px; color: var(--ath-olive) !important;
        box-shadow:0 4px 12px rgba(0,0,0,.05); margin:6px 0 10px; 
      }
      .ath-banner .title{ font-weight:800; margin:0; color: var(--ath-olive) !important; }
      .ath-banner .sub{ margin:2px 0 0; color: var(--ath-muted) !important; }

      /* Progress bar */
      .stProgress > div > div > div > div { background-color: var(--ath-olive); }

      /* Headings */
      h1, h2, h3, h4, .stMarkdown h2, .stMarkdown h3 {
        color: var(--ath-olive-dark) !important;
        font-weight: 800 !important;
        letter-spacing: .2px;
      }

      /* Analysis wrapper */
      .analysis-wrap{ min-height: 72px; }

      /* Textarea placeholder */
      .stTextArea textarea::placeholder {
        color: var(--ath-muted) !important;
        opacity: .8 !important;
      }

      /* SIMPLE, FUNCTIONAL UPLOAD STYLING */
      /* Style the actual file uploader dropzone to be clean and match our design */
      [data-testid="stFileUploader"] {
        border: 2px dashed var(--ath-border) !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background: var(--ath-surface) !important;
      }

      [data-testid="stFileUploader"]:hover {
        border-color: var(--ath-amber) !important;
        background: #FFFBF3 !important;
      }

      /* Style the drag and drop text */
      [data-testid="stFileUploaderDropzone"] > div > div {
        color: var(--ath-olive-dark) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
      }

      /* Style the browse button */
      [data-testid="stFileUploader"] button {
        color: var(--ath-olive-dark) !important;
        background-color: var(--ath-surface) !important;
        border: 1px solid var(--ath-border) !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        margin-top: 8px !important;
      }

      [data-testid="stFileUploader"] button:hover {
        border-color: var(--ath-amber) !important;
        background-color: #FFFBF3 !important;
      }

      /* File uploader file name and size */
      [data-testid="stFileUploaderFileName"],
      [data-testid="stFileUploaderFileSize"] {
        color: var(--ath-olive-dark) !important;
      }

      /* Clean upload header */
      .upload-header {
        text-align: center;
        margin-bottom: 15px;
      }

      .upload-title {
        color: var(--ath-olive-dark) !important;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 4px;
      }

      .upload-subtitle {
        color: var(--ath-olive) !important;
        font-size: 0.85rem;
        line-height: 1.4;
      }

      /* Fix for analysis text colors */
      .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol,
      .stMarkdown div, .stMarkdown span,
      .element-container .stMarkdown,
      div[data-testid="stVerticalBlock"] .stMarkdown {
        color: var(--ath-olive-dark) !important;
      }

      /* Fix Streamlit warning/error/info boxes */
      .stAlert {
        color: var(--ath-olive-dark) !important;
      }

      .stWarning {
        background-color: #FFFBF3 !important;
        border-left: 4px solid var(--ath-amber) !important;
        color: var(--ath-olive-dark) !important;
      }

      .stError {
        background-color: #FEF2F2 !important;
        border-left: 4px solid var(--ath-terr) !important;
        color: var(--ath-olive-dark) !important;
      }

      .stInfo {
        background-color: #F0F9FF !important;
        border-left: 4px solid var(--ath-olive) !important;
        color: var(--ath-olive-dark) !important;
      }

      /* Fix button text */
      .stButton button {
        color: var(--ath-olive-dark) !important;
      }
    </style>
    """, unsafe_allow_html=True)


# ---------- main UI ----------
def main_dashboard():
    st.set_page_config(
        page_title="RFP Intelligence Pro",
        layout="wide",
        page_icon="ui/logo_Athari.png"
    )

    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'last_uploaded_file' not in st.session_state:
        st.session_state.last_uploaded_file = None
    if 'organization_profile' not in st.session_state:
        st.session_state.organization_profile = ""
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False

    _inject_css()

    # --- HERO (centered with logo) ---
    logo_b64 = _load_logo_b64()
    st.markdown(f"""
    <div class="main-header">
      <div class="hero-center">
        {f'<img class="hero-logo" src="data:image/png;base64,{logo_b64}">' if logo_b64 else ''}
        <h1 class="hero-title">Atharii AI-Powered RFP Analyzer</h1>
        <p class="hero-sub">Advanced AI-Powered RFP Analysis Platform by <b>Atharii</b></p>
        <div class="hero-chips">
          <span class="hero-chip">9 AI Models</span>
          <span class="hero-chip">Multi-Stage Analysis</span>
          <span class="hero-chip">98% Success Rate</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Upload center ---
    st.markdown('<div class="section-card"><h4>Document Upload Center</h4>', unsafe_allow_html=True)
    uploaded_file, organization_profile = handle_file_uploads()
    st.markdown('</div>', unsafe_allow_html=True)

    # ✅ Fixed results slot (prevents jump when analysis renders)
    analysis_area = st.container()

    # --- CTA (always visible; validate inside) ---
    clicked = st.button("Launch Comprehensive Analysis", key="analyze_btn", type="primary")

    if clicked:
        if not uploaded_file:
            st.warning("Please upload an RFP file first.")
        else:
            with analysis_area:
                perform_analysis(uploaded_file, organization_profile or "")

    # If no new file but we have old results, let users view them explicitly
    if not uploaded_file and st.session_state.analysis_results:
        st.info("Previous analysis results are available below.")
        if st.button("View Previous Analysis", key="view_previous"):
            with analysis_area:
                display_previous_analysis()


def handle_file_uploads():
    left, right = st.columns(2)

    # -------- Left: RFP --------
    with left:
        st.markdown('<div class="upload-tile">', unsafe_allow_html=True)

        # Simple header for RFP upload
        st.markdown("""
        <div class="upload-header">
            <div class="upload-title">RFP Document</div>
            <div class="upload-subtitle">Upload your RFP for comprehensive analysis</div>
        </div>
        """, unsafe_allow_html=True)

        # The actual file uploader - FULLY FUNCTIONAL
        rfp_file = st.file_uploader(
            "Drag and drop file here",
            type=AppConfig.SUPPORTED_FILE_TYPES,
            key="rfp_uploader",
            help=f"Supported formats: PDF, DOCX, TXT • Max size: {AppConfig.MAX_FILE_SIZE_MB}MB"
        )

        if rfp_file and not _validate_file_upload(rfp_file):
            rfp_file = None

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- Right: Organization (optional) --------
    with right:
        st.markdown('<div class="upload-tile">', unsafe_allow_html=True)

        # Simple header for Organization upload
        st.markdown("""
        <div class="upload-header">
            <div class="upload-title">Organization Profile</div>
            <div class="upload-subtitle">Upload your organization profile for compatibility analysis</div>
        </div>
        """, unsafe_allow_html=True)

        # The actual file uploader - FULLY FUNCTIONAL
        org_file = st.file_uploader(
            "Drag and drop file here",
            type=AppConfig.SUPPORTED_FILE_TYPES,
            key="org_uploader",
            help=f"Supported formats: PDF, DOCX, TXT • Max size: {AppConfig.MAX_FILE_SIZE_MB}MB"
        )

        if org_file and not _validate_file_upload(org_file):
            org_file = None

        st.markdown('<div class="or-divider"><span>or describe your organization</span></div>',
                    unsafe_allow_html=True)

        org_description = st.text_area(
            "Or describe your organization (optional)…",
            placeholder=("e.g., We are a community health nonprofit with 12+ years delivering "
                         "harm-reduction, MAT linkage, and peer recovery services statewide..."),
            height=140,
            key="org_description"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- Resolve organization profile --------
    organization_profile = ""
    if org_file:
        with st.spinner("Processing organization profile..."):
            try:
                organization_profile = process_uploaded_file(org_file)
                if not organization_profile or len(organization_profile.strip()) < AppConfig.MIN_TEXT_LENGTH:
                    st.warning("Organization profile file appears to be empty or too short.")
                    organization_profile = ""
            except Exception as e:
                st.error(f"Error processing organization profile: {str(e)}")
                organization_profile = ""
    elif org_description:
        organization_profile = org_description

    return rfp_file, organization_profile


def perform_analysis(uploaded_file, organization_profile):
    """Perform comprehensive RFP analysis with progress tracking and error handling."""
    progress_bar = None
    status_text = None

    try:
        # Setup progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step, total_steps=4, message=""):
            progress = (step / total_steps)
            progress_bar.progress(progress)
            if message:
                status_text.text(message)

        # Step 1: File processing
        update_progress(1, message="Processing uploaded file...")
        raw_text = process_uploaded_file(uploaded_file)

        if not raw_text or len(raw_text.strip()) < AppConfig.MIN_TEXT_LENGTH:
            st.error(
                f"Uploaded file appears to be empty or too short for analysis. Minimum required: {AppConfig.MIN_TEXT_LENGTH} characters")
            if progress_bar:
                progress_bar.empty()
            if status_text:
                status_text.empty()
            return

        # Step 2: Text cleaning
        update_progress(2, message="Cleaning and preparing text...")
        text = clean_text(raw_text)

        if not text or len(text.strip()) < AppConfig.MIN_TEXT_LENGTH:
            st.error("Text cleaning resulted in insufficient content for analysis")
            if progress_bar:
                progress_bar.empty()
            if status_text:
                status_text.empty()
            return

        # Step 3: AI Analysis
        update_progress(3, message="Running multi-stage AI analysis...")
        results = multi_stage_rfp_analysis(text, organization_profile)

        # Step 4: Store results and complete
        update_progress(4, message="Finalizing analysis...")
        st.session_state.analysis_results = results
        st.session_state.organization_profile = organization_profile
        st.session_state.last_uploaded_file = uploaded_file.name

        # Small delay to show completion
        time.sleep(0.5)

        # Clear progress indicators
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()

        # Display success banner and results
        status_area = st.container()
        status_area.markdown("""
        <div class="ath-banner analysis-wrap">
          <div>
            <div class="title">Comprehensive analysis complete.</div>
            <div class="sub">Your RFP has been analyzed across all critical dimensions.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Render the tabs with results
        display_all_tabs(results, organization_profile)

    except Exception as e:
        # Clear progress indicators in case of error
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()

        st.error(f"Analysis failed: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

        # Log the error for debugging
        config = AppConfig()
        if config.DEBUG:
            st.exception(e)


def display_previous_analysis():
    """Display previously stored analysis results."""
    if st.session_state.analysis_results:
        st.markdown("""
        <div class="ath-banner analysis-wrap">
          <div>
            <div class="title">Previous analysis results</div>
            <div class="sub">Displaying analysis from your last session.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        display_all_tabs(
            st.session_state.analysis_results,
            st.session_state.organization_profile
        )
    else:
        st.warning("No previous analysis results found.")


# Add a main guard for direct execution
if __name__ == "__main__":
    main_dashboard()