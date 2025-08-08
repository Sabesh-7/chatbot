import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json
import hashlib
import os
from typing import List, Dict, Any
import logging
from config import Config

# Configure logging
logger = logging.getLogger(__name__)

class CollegeChatbot:
    def __init__(self):
        self.setup_pinecone()
        self.setup_embeddings()
        
    def setup_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            # Get API key from environment or Streamlit secrets
            api_key = st.secrets.get("PINECONE_API_KEY") or Config.PINECONE_API_KEY
            if not api_key:
                logger.error("Pinecone API key not found")
                st.error("Pinecone API key not found. Please add it to your .env file or Streamlit secrets.")
                return
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=api_key)
            logger.info("Pinecone client initialized successfully")
            
            # Create or connect to index
            index_name = Config.PINECONE_INDEX_NAME
            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
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
            logger.info("Pinecone index connected successfully")
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone: {str(e)}")
            st.error(f"Error setting up Pinecone: {str(e)}")
            
    def setup_embeddings(self):
        """Initialize sentence transformer model"""
        try:
            logger.info("Loading sentence transformer model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            st.error(f"Error loading embedding model: {str(e)}")
    
    def add_document(self, content: str, category: str, metadata: Dict[str, Any]):
        """Add document to Pinecone index"""
        try:
            logger.info(f"Adding document to category: {category}")
            
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
            logger.info(f"Document added successfully with ID: {doc_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            st.error(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        try:
            logger.info(f"Searching for query: {query[:50]}...")
            
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            logger.info(f"Found {len(results.matches)} matches for query")
            return results.matches
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def generate_response(self, query: str) -> str:
        """Generate response based on search results"""
        # Search for relevant documents
        matches = self.search_documents(query)
        
        if not matches:
            return "I'm sorry, I don't have information on that at the moment. Please check with your college administration."
        
        # Similarity threshold for matching
        similarity_threshold = 0.5
        
        # Find best match above threshold
        best_match = matches[0] if matches else None
        
        if not best_match or best_match.score < similarity_threshold:
            return "I'm sorry, I don't have information on that at the moment. Please check with your college administration."
        
        # Combine relevant content from matches above threshold
        relevant_content = []
        for match in matches:
            if match.score >= similarity_threshold:
                content = match.metadata.get('content', '')
                title = match.metadata.get('title', '')
                relevant_content.append(f"**{title}**: {content}")
        
        if not relevant_content:
            return "I'm sorry, I don't have information on that at the moment. Please check with your college administration."
        
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