import logging
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

logger = logging.getLogger(__name__)

class User:
    def __init__(self, username, email, password_hash=None, role='student', 
                 first_name=None, last_name=None, is_active=True, 
                 created_at=None, last_login=None, _id=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash or ""
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
    
    def set_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def id(self):
        """Compatibility property for id attribute"""
        return self._id
    
    def to_dict(self):
        """Convert user object to dictionary for MongoDB"""
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user object from MongoDB document"""
        return cls(
            _id=data.get('_id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash', ""),
            role=data.get('role'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )

def create_mongodb_client():
    """Create MongoDB client"""
    try:
        client = MongoClient(Config.MONGODB_URI)
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

def get_database():
    """Get MongoDB database"""
    client = create_mongodb_client()
    return client[Config.MONGODB_DATABASE]

def get_collection():
    """Get MongoDB collection"""
    db = get_database()
    return db[Config.MONGODB_COLLECTION]

def init_database():
    """Initialize database and create default admin user"""
    try:
        logger.info("Initializing MongoDB database...")
        
        client = create_mongodb_client()
        db = client[Config.MONGODB_DATABASE]
        collection = db[Config.MONGODB_COLLECTION]
        
        # Create indexes
        collection.create_index("username", unique=True)
        collection.create_index("email", unique=True)
        
        logger.info("MongoDB database initialized successfully")
        
        # Create default admin user if it doesn't exist
        admin_user = collection.find_one({"username": "admin"})
        if not admin_user:
            logger.info("Creating default admin user")
            admin_user_obj = User(
                username='admin',
                email='admin@college.edu',
                role='admin',
                first_name='Admin',
                last_name='User'
            )
            admin_user_obj.set_password('admin123')
            
            collection.insert_one(admin_user_obj.to_dict())
            logger.info("Default admin user created: admin/admin123")
        else:
            logger.info("Default admin user already exists")
            
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB database: {e}")
        raise 