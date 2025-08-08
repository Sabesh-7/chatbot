import streamlit as st
import logging
import os
from src.database.models import init_database
from src.ui.interfaces import login_interface, admin_interface, student_interface
from logging_config import setup_logging

# Setup logging
logger = setup_logging()

def main():
    """Main application"""
    st.set_page_config(
        page_title="College Assistant",
        page_icon="🏫",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        st.error("Failed to initialize database. Please check your configuration.")
        return
    
    # Check authentication
    if not st.session_state.authenticated:
        login_interface()
    else:
        # Sidebar with user info and logout
        with st.sidebar:
            if st.session_state.username:
                st.write(f"👋 Welcome, {st.session_state.username}!")
                st.write(f"Role: {st.session_state.user_role.title()}")
            else:
                st.write("👋 Welcome!")
                st.write("Please log in")
            
            if st.button("Logout", key="logout_btn"):
                st.session_state.authenticated = False
                st.session_state.user_role = None
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.chat_history = []
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 Categories")
            st.markdown("- Placements")
            st.markdown("- Events") 
            st.markdown("- Academics")
            st.markdown("- Exams")
            st.markdown("- Clubs")
            st.markdown("- Announcements")
        
        # Route to appropriate interface
        if st.session_state.user_role == "admin":
            admin_interface()
        else:
            student_interface()

if __name__ == "__main__":
    main() 