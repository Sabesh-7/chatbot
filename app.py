import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import openai
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from datetime import datetime
import json
import hashlib
import os
from typing import List, Dict, Any

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

class CollegeChatbot:
    def __init__(self):
        self.setup_pinecone()
        self.setup_embeddings()
        
    def setup_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            # Get API key from environment or Streamlit secrets
            api_key = st.secrets.get("PINECONE_API_KEY") or os.getenv("PINECONE_API_KEY")
            if not api_key:
                st.error("Pinecone API key not found. Please add it to your secrets.")
                return
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=api_key)
            
            # Create or connect to index
            index_name = "college-info"
            if index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=index_name,
                    dimension=384,  # for sentence-transformers model
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            
            self.index = self.pc.Index(index_name)
            
        except Exception as e:
            st.error(f"Error setting up Pinecone: {str(e)}")
            
    def setup_embeddings(self):
        """Initialize sentence transformer model"""
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            st.error(f"Error loading embedding model: {str(e)}")
    
    def add_document(self, content: str, category: str, metadata: Dict[str, Any]):
        """Add document to Pinecone index"""
        try:
            # Generate embedding
            embedding = self.embedder.encode(content).tolist()
            
            # Create unique ID
            doc_id = hashlib.md5(f"{content[:100]}{datetime.now()}".encode()).hexdigest()
            
            # Add metadata
            metadata.update({
                'content': content,
                'category': category,
                'timestamp': datetime.now().isoformat()
            })
            
            # Upsert to Pinecone
            self.index.upsert([(doc_id, embedding, metadata)])
            
            return True
            
        except Exception as e:
            st.error(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Debug: Print search results
            st.write("🔍 **Debug - Search Results:**")
            for i, match in enumerate(results.matches):
                st.write(f"Match {i+1}: Score = {match.score:.3f}, Title = {match.metadata.get('title', 'N/A')}")
            
            return results.matches
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def generate_response(self, query: str) -> str:
        """Generate response based on search results"""
        # Search for relevant documents
        matches = self.search_documents(query)
        
        # Debug information
        st.write(f"🔍 **Debug Info:**")
        st.write(f"- Query: '{query}'")
        st.write(f"- Number of matches found: {len(matches)}")
        
        if not matches:
            return "I'm sorry, I don't have information on that at the moment. Please check with your college administration. (No matches found)"
        
        # Lower similarity threshold for better matching
        similarity_threshold = 0.5  # Reduced from 0.7 to 0.5
        
        # Find best match above threshold
        best_match = matches[0] if matches else None
        st.write(f"- Best match score: {best_match.score:.3f}")
        st.write(f"- Similarity threshold: {similarity_threshold}")
        
        if not best_match or best_match.score < similarity_threshold:
            return f"I'm sorry, I don't have information on that at the moment. Please check with your college administration. (Best match score: {best_match.score:.3f}, threshold: {similarity_threshold})"
        
        # Combine relevant content from matches above threshold
        relevant_content = []
        for match in matches:
            if match.score >= similarity_threshold:
                content = match.metadata.get('content', '')
                title = match.metadata.get('title', '')
                relevant_content.append(f"**{title}**: {content}")
        
        if not relevant_content:
            return f"I'm sorry, I don't have information on that at the moment. Please check with your college administration. (No content above threshold)"
        
        # Create formatted response
        response = "Based on the college information:\n\n" + "\n\n".join(relevant_content[:2])
        
        # Limit response length
        if len(response) > 800:
            response = response[:800] + "..."
        
        return response
    
    def _format_response(self, context: str, query: str) -> str:
        """Format response based on context - keeping for backward compatibility"""
        if len(context.strip()) > 0:
            return f"Based on the college information:\n\n{context[:500]}{'...' if len(context) > 500 else ''}"
        else:
            return "I'm sorry, I don't have information on that at the moment. Please check with your college administration."

def authenticate_user(username: str, password: str, role: str) -> bool:
    """Simple authentication system"""
    # In production, use proper authentication with hashed passwords
    users = {
        'admin': {'password': 'admin123', 'role': 'admin'},
        'student': {'password': 'student123', 'role': 'student'},
        'staff': {'password': 'staff123', 'role': 'staff'}
    }
    
    if username in users and users[username]['password'] == password and users[username]['role'] == role:
        return True
    return False

def admin_interface():
    """Admin interface for managing college data"""
    st.header("🔧 Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["Add Information", "Manage Documents", "View Analytics"])
    
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
        
        if st.button("Add Information", type="primary"):
            if title and content:
                chatbot = CollegeChatbot()
                metadata = {
                    'title': title,
                    'department': department,
                    'date': str(date) if date else None
                }
                
                if chatbot.add_document(content, category, metadata):
                    st.success("Information added successfully!")
                else:
                    st.error("Failed to add information.")
            else:
                st.error("Please fill in both title and content.")
    
    with tab2:
        st.subheader("Document Management")
        st.info("Document management features coming soon...")
        
    with tab3:
        st.subheader("Analytics")
        st.info("Analytics dashboard coming soon...")

def student_interface():
    """Student interface for querying information"""
    st.header("🎓 College Assistant")
    st.write("Ask me anything about college information!")
    
    # Initialize chatbot
    chatbot = CollegeChatbot()
    
    # Add debug toggle
    debug_mode = st.toggle("🔧 Debug Mode", help="Show search scores and debug information")
    
    # Index statistics
    with st.expander("📊 Index Statistics"):
        try:
            stats = chatbot.index.describe_index_stats()
            st.write(f"**Total vectors in index:** {stats.get('total_vector_count', 'Unknown')}")
            st.write(f"**Index dimension:** {stats.get('dimension', 'Unknown')}")
        except Exception as e:
            st.error(f"Could not retrieve index stats: {str(e)}")
    
    # Chat interface
    if prompt := st.chat_input("Ask your question..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.spinner("Searching for information..."):
            if debug_mode:
                st.write("### 🔍 Debug Information")
            response = chatbot.generate_response(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Display chat history (but filter out debug info for clean display)
    st.write("### 💬 Chat History")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Quick action buttons
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Placement Statistics"):
            st.session_state.chat_history.append({"role": "user", "content": "What are the latest placement statistics?"})
            response = chatbot.generate_response("What are the latest placement statistics?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("📅 Upcoming Events"):
            st.session_state.chat_history.append({"role": "user", "content": "What are the upcoming events?"})
            response = chatbot.generate_response("What are the upcoming events?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📚 Exam Schedule"):
            st.session_state.chat_history.append({"role": "user", "content": "What is the exam schedule?"})
            response = chatbot.generate_response("What is the exam schedule?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

def login_interface():
    """Login interface"""
    st.title("🏫 College Assistant Chatbot")
    st.subheader("Please Login")
    
    col1, col2 = st.columns([1, 2])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["student", "staff", "admin"])
            
            if st.form_submit_button("Login", type="primary"):
                if authenticate_user(username, password, role):
                    st.session_state.authenticated = True
                    st.session_state.user_role = role
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
    
    with col1:
        st.info("""
        **Demo Credentials:**
        
        **Admin:**
        - Username: admin
        - Password: admin123
        
        **Student:**
        - Username: student  
        - Password: student123
        
        **Staff:**
        - Username: staff
        - Password: staff123
        """)

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
    
    # Check authentication
    if not st.session_state.authenticated:
        login_interface()
    else:
        # Sidebar with user info and logout
        with st.sidebar:
            st.write(f"👋 Welcome, {st.session_state.user_role.title()}!")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_role = None
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