import streamlit as st
import logging
from datetime import datetime
from src.database.auth import authenticate_user, create_user, update_user_password, get_all_users
from src.chatbot.college_chatbot import CollegeChatbot

# Configure logging
logger = logging.getLogger(__name__)

def admin_interface():
    """Admin interface for managing college data"""
    st.header("🔧 Admin Panel")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Add Information", "User Management", "Manage Documents", "View Analytics"])
    
    with tab1:
        st.subheader("Add College Information")
        
        category = st.selectbox("Category", [
            "Placements", "Events", "Academics", "Exams", 
            "Clubs", "Announcements", "Other"
        ])
        
        title = st.text_input("Title")
        content = st.text_area("Content", height=200)
        
        # Additional metadata
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date (if applicable)")
        with col2:
            department = st.text_input("Department (optional)")
        
        if st.button("Add Information", type="primary", key="add_info_btn"):
            if title and content:
                try:
                    logger.info(f"Adding information: {title} to category: {category}")
                    chatbot = CollegeChatbot()
                    metadata = {
                        'title': title,
                        'department': department,
                        'date': str(date) if date else None
                    }
                    
                    if chatbot.add_document(content, category, metadata):
                        logger.info(f"Information added successfully: {title}")
                        st.success("Information added successfully!")
                    else:
                        logger.error(f"Failed to add information: {title}")
                        st.error("Failed to add information.")
                except Exception as e:
                    logger.error(f"Error adding information: {str(e)}")
                    st.error("Error adding information. Please try again.")
            else:
                st.error("Please fill in both title and content.")
    
    with tab2:
        st.subheader("User Management")
        
        # Password reset section
        st.write("### Reset User Password")
        reset_username = st.text_input("Username to reset password for")
        new_password = st.text_input("New Password", type="password", key="reset_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_reset_password")
        
        if st.button("Reset Password", key="reset_btn"):
            if reset_username and new_password and confirm_new_password:
                if new_password == confirm_new_password:
                    if len(new_password) >= 6:
                        try:
                            logger.info(f"Password reset attempt for user: {reset_username}")
                            if update_user_password(reset_username, new_password):
                                logger.info(f"Password reset successful for user: {reset_username}")
                                st.success(f"Password updated successfully for user: {reset_username}")
                            else:
                                logger.warning(f"Password reset failed - user not found: {reset_username}")
                                st.error("User not found!")
                        except Exception as e:
                            logger.error(f"Password reset error for user {reset_username}: {str(e)}")
                            st.error("Password reset failed. Please try again.")
                    else:
                        st.error("Password must be at least 6 characters long!")
                else:
                    st.error("Passwords do not match!")
            else:
                st.error("Please fill in all fields!")
        
        st.markdown("---")
        
        # User list section
        st.write("### User List")
        try:
            users = get_all_users()
            if users:
                user_data = []
                for user in users:
                    user_data.append({
                        "Username": user.username,
                        "Email": user.email,
                        "Role": user.role.title(),
                        "Status": "Active" if user.is_active else "Inactive",
                        "Created": user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
                    })
                st.dataframe(user_data, use_container_width=True)
            else:
                st.info("No users found.")
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            st.error("Error fetching user list.")
    
    with tab3:
        st.subheader("Document Management")
        st.info("Document management features coming soon...")
        
    with tab4:
        st.subheader("Analytics")
        st.info("Analytics dashboard coming soon...")

def student_interface():
    """Student interface for querying information"""
    st.header("🎓 College Assistant")
    st.write("Ask me anything about college information!")
    
    # Initialize chatbot
    chatbot = CollegeChatbot()
    
    # Chat interface
    if prompt := st.chat_input("Ask your question..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Generate response
        try:
            username = st.session_state.username or "user"
            logger.info(f"Chat query from user {username}: {prompt[:50]}...")
            with st.spinner("Searching for information..."):
                response = chatbot.generate_response(prompt)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            logger.info(f"Response generated successfully for user {username}")
        except Exception as e:
            username = st.session_state.username or "user"
            logger.error(f"Error generating response for user {username}: {str(e)}")
            error_response = "I'm sorry, I encountered an error while processing your request. Please try again."
            st.session_state.chat_history.append({"role": "assistant", "content": error_response})
            st.error("Error processing your request. Please try again.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Quick action buttons
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("\U0001F4CA Placement Statistics", key="placement_btn"):
            try:
                username = st.session_state.username or "user"
                logger.info(f"Quick action - Placement Statistics by user {username}")
                st.session_state.chat_history.append({"role": "user", "content": "What are the latest placement statistics?"})
                response = chatbot.generate_response("What are the latest placement statistics?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                logger.error(f"Error in placement statistics quick action: {str(e)}")
                st.error("Error processing request. Please try again.")
    
    with col2:
        if st.button("\U0001F4C5 Upcoming Events", key="events_btn"):
            try:
                username = st.session_state.username or "user"
                logger.info(f"Quick action - Upcoming Events by user {username}")
                st.session_state.chat_history.append({"role": "user", "content": "What are the upcoming events?"})
                response = chatbot.generate_response("What are the upcoming events?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                logger.error(f"Error in upcoming events quick action: {str(e)}")
                st.error("Error processing request. Please try again.")
    
    with col3:
        if st.button("\U0001F4DA Exam Schedule", key="exam_btn"):
            try:
                username = st.session_state.username or "user"
                logger.info(f"Quick action - Exam Schedule by user {username}")
                st.session_state.chat_history.append({"role": "user", "content": "What is the exam schedule?"})
                response = chatbot.generate_response("What is the exam schedule?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                logger.error(f"Error in exam schedule quick action: {str(e)}")
                st.error("Error processing request. Please try again.")

def login_interface():
    """Login interface"""
    st.title("🏫 College Assistant Chatbot")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Please Login")
        
        col1, col2 = st.columns([1, 2])
        
        with col2:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", type="primary"):
                    if username and password:
                        try:
                            logger.info(f"Login attempt for user: {username}")
                            user = authenticate_user(username, password)
                            if user:
                                st.session_state.authenticated = True
                                st.session_state.user_role = user.role
                                st.session_state.user_id = user._id
                                st.session_state.username = user.username
                                logger.info(f"User {username} logged in successfully as {user.role}")
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                logger.warning(f"Failed login attempt for user: {username}")
                                st.error("Invalid username or password!")
                        except Exception as e:
                            logger.error(f"Login error for user {username}: {str(e)}")
                            st.error("Login failed. Please try again.")
                    else:
                        st.error("Please enter both username and password!")
        
        with col1:
            st.info("""
            Welcome! Please login or register for a new account.
            If you are an admin, use your assigned credentials.
            """)
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username", key="reg_username")
                email = st.text_input("Email", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_password")
            
            with col2:
                first_name = st.text_input("First Name", key="reg_first_name")
                last_name = st.text_input("Last Name", key="reg_last_name")
                role = st.selectbox("Role", ["student", "staff"], key="reg_role")
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            
            if st.form_submit_button("Register", type="primary"):
                if username and email and password and first_name and last_name:
                    if password == confirm_password:
                        if len(password) >= 6:
                            try:
                                logger.info(f"Registration attempt for user: {username}")
                                if create_user(username, email, password, role, first_name, last_name):
                                    logger.info(f"User {username} registered successfully")
                                    st.success("Account created successfully! You can now login.")
                                else:
                                    logger.warning(f"Registration failed - user/email already exists: {username}")
                                    st.error("Username or email already exists!")
                            except Exception as e:
                                logger.error(f"Registration error for user {username}: {str(e)}")
                                st.error("Registration failed. Please try again.")
                        else:
                            st.error("Password must be at least 6 characters long!")
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.error("Please fill in all required fields!") 