import logging
from datetime import datetime
from .models import User, get_collection

logger = logging.getLogger(__name__)

def authenticate_user(username: str, password: str) -> User:
    """Authenticate user and return user object if successful"""
    try:
        logger.info(f"Authenticating user: {username}")
        collection = get_collection()
        
        user_data = collection.find_one({"username": username, "is_active": True})
        if user_data:
            user = User.from_dict(user_data)
            if user.check_password(password):
                # Update last login
                collection.update_one(
                    {"_id": user._id},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                logger.info(f"User {username} authenticated successfully")
                return user
        
        logger.warning(f"Authentication failed for user: {username}")
        return None
    except Exception as e:
        logger.error(f"Authentication error for user {username}: {e}")
        return None

def create_user(username: str, email: str, password: str, role: str = 'student', 
                first_name: str = None, last_name: str = None) -> bool:
    """Create a new user"""
    try:
        logger.info(f"Creating new user: {username}")
        collection = get_collection()
        
        # Check if user already exists
        existing_user = collection.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })
        
        if existing_user:
            logger.warning(f"User creation failed - user/email already exists: {username}")
            return False
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        collection.insert_one(user.to_dict())
        logger.info(f"User {username} created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        return False

def get_user_by_username(username: str) -> User:
    """Get user by username"""
    try:
        collection = get_collection()
        user_data = collection.find_one({"username": username})
        if user_data:
            return User.from_dict(user_data)
        return None
    except Exception as e:
        logger.error(f"Error getting user {username}: {e}")
        return None

def update_user_password(username: str, new_password: str) -> bool:
    """Update user password"""
    try:
        logger.info(f"Updating password for user: {username}")
        collection = get_collection()
        
        user_data = collection.find_one({"username": username})
        if user_data:
            user = User.from_dict(user_data)
            user.set_password(new_password)
            
            collection.update_one(
                {"_id": user._id},
                {"$set": {"password_hash": user.password_hash}}
            )
            logger.info(f"Password updated successfully for user: {username}")
            return True
        
        logger.warning(f"Password update failed - user not found: {username}")
        return False
    except Exception as e:
        logger.error(f"Error updating password for user {username}: {e}")
        return False

def get_all_users():
    """Get all users (for admin panel)"""
    try:
        collection = get_collection()
        users_data = collection.find({})
        users = []
        for user_data in users_data:
            users.append(User.from_dict(user_data))
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []

def deactivate_user(username: str) -> bool:
    """Deactivate a user account"""
    try:
        logger.info(f"Deactivating user: {username}")
        collection = get_collection()
        
        result = collection.update_one(
            {"username": username},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count > 0:
            logger.info(f"User {username} deactivated successfully")
            return True
        
        logger.warning(f"User deactivation failed - user not found: {username}")
        return False
    except Exception as e:
        logger.error(f"Error deactivating user {username}: {e}")
        return False 