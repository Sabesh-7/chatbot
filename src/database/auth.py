import logging
from datetime import datetime
from sqlalchemy.orm import Session
from .models import User, create_session

# Configure logging for authentication operations
logger = logging.getLogger(__name__)

def authenticate_user(username: str, password: str) -> User:
    """Authenticate user and return user object if successful"""
    session = create_session()
    try:
        logger.info(f"Authenticating user: {username}")
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()
            logger.info(f"User {username} authenticated successfully")
            
            # Create a new user object with the session data to avoid detached instance issues
            authenticated_user = User(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login
            )
            return authenticated_user
        logger.warning(f"Authentication failed for user: {username}")
        return None
    except Exception as e:
        logger.error(f"Authentication error for user {username}: {e}")
        return None
    finally:
        session.close()

def create_user(username: str, email: str, password: str, role: str = 'student', 
                first_name: str = None, last_name: str = None) -> bool:
    """Create a new user"""
    session = create_session()
    try:
        logger.info(f"Creating new user: {username}")
        
        # Check if user already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
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
        
        session.add(user)
        session.commit()
        logger.info(f"User {username} created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_user_by_username(username: str) -> User:
    """Get user by username"""
    session = create_session()
    try:
        return session.query(User).filter_by(username=username).first()
    finally:
        session.close()

def update_user_password(username: str, new_password: str) -> bool:
    """Update user password"""
    session = create_session()
    try:
        logger.info(f"Updating password for user: {username}")
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            session.commit()
            logger.info(f"Password updated successfully for user: {username}")
            return True
        logger.warning(f"Password update failed - user not found: {username}")
        return False
    except Exception as e:
        logger.error(f"Error updating password for user {username}: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_all_users():
    """Get all users (for admin panel)"""
    session = create_session()
    try:
        return session.query(User).all()
    finally:
        session.close()

def deactivate_user(username: str) -> bool:
    """Deactivate a user account"""
    session = create_session()
    try:
        logger.info(f"Deactivating user: {username}")
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.is_active = False
            session.commit()
            logger.info(f"User {username} deactivated successfully")
            return True
        logger.warning(f"User deactivation failed - user not found: {username}")
        return False
    except Exception as e:
        logger.error(f"Error deactivating user {username}: {e}")
        session.rollback()
        return False
    finally:
        session.close() 