import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt
from config import Config

# Configure logging for database operations
logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='student')  # student, staff, admin
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    def set_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

def create_database_engine():
    """Create SQLAlchemy engine based on configuration"""
    database_url = Config.get_database_url()
    
    if Config.DB_TYPE == 'sqlite':
        return create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        return create_engine(database_url)

def create_session():
    """Create database session"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """Initialize database tables"""
    try:
        logger.info(f"Initializing {Config.DB_TYPE} database...")
        engine = create_database_engine()
        Base.metadata.create_all(engine)
        logger.info(f"{Config.DB_TYPE} database tables created successfully")
        
        # Create default admin user if it doesn't exist
        session = create_session()
        try:
            admin_user = session.query(User).filter_by(username='admin').first()
            if not admin_user:
                logger.info("Creating default admin user")
                admin_user = User(
                    username='admin',
                    email='admin@college.edu',
                    role='admin',
                    first_name='Admin',
                    last_name='User'
                )
                admin_user.set_password('admin123')
                session.add(admin_user)
                session.commit()
                logger.info("Default admin user created: admin/admin123")
            else:
                logger.info("Default admin user already exists")
        except Exception as e:
            logger.error(f"Error creating default admin user: {e}")
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Failed to initialize {Config.DB_TYPE} database: {e}")
        raise 