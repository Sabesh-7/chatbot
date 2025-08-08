import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database Configuration
    DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # 'postgresql' or 'sqlite'
    
    # PostgreSQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'college_chatbot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    # SQLite Configuration
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'data/college_chatbot.db')
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'college-info')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    @classmethod
    def get_database_url(cls):
        """Get database URL based on configuration"""
        if cls.DB_TYPE == 'postgresql':
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(cls.SQLITE_DB_PATH), exist_ok=True)
            return f"sqlite:///{cls.SQLITE_DB_PATH}" 