import streamlit as st
from logging_config import setup_logging
from src.database.models import init_database
from src.ui.interfaces import login_interface, admin_interface, student_interface

# Setup logging
logger = setup_logging()
logger.info("Logging system initialized")

# Initialize database
try:
    init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    st.error("Database initialization failed. Please check your configuration.")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main application logic
if not st.session_state.authenticated:
    login_interface()
else:
    if st.session_state.user_role == 'admin':
        admin_interface()
    else:
        student_interface() 