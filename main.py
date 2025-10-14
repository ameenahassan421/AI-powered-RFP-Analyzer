import streamlit as st
from ui.dashboard import main_dashboard

# Initialize session state
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False
if 'organization_profile' not in st.session_state:
    st.session_state.organization_profile = None

if __name__ == "__main__":
    main_dashboard()
