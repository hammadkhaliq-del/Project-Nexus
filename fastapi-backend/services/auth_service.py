"""
Authentication Service
Handles user management and token operations
"""
from typing import Optional, Dict
from datetime import datetime

from models.user import User, UserCreate, UserInDB, UserResponse
from utils.security import hash_password, verify_password, create_token, verify_token
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthService: 
    """
    Authentication service for user management
    Uses in-memory storage (replace with database in production)
    """
    
    def __init__(self):
        # In-memory user storage
        self.users: Dict[str, UserInDB] = {}
        self.email_index: Dict[str, str] = {}  # email -> username mapping
        
        logger.info("AuthService initialized")
    
    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """
        Create a new user
        
        Args:
            user_data: User creation data
        
        Returns:
            Created user response or None if validation fails
        """
        # Check username exists
        if user_data.username in self.users:
            logger.warning(f"Username already exists: {user_data.username}")
            return None
        
        # Check email exists
        if user_data.email in self. email_index:
            logger. warning(f"Email already registered: {user_data.email}")
            return None
        
        # Hash password
        hashed_pw = hash_password(user_data.password)
        
        # Create user in DB
        user_in_db = UserInDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_pw,
            created_at=datetime.utcnow()
        )
        
        # Store user
        self.users[user_data.username] = user_in_db
        self.email_index[user_data.email] = user_data.username
        
        logger.info(f"User created: {user_data.username}")
        
        return UserResponse(
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            created_at=user_in_db.created_at
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User if authenticated, None otherwise
        """
        user = self.users.get(username)
        
        if not user: 
            logger.warning(f"User not found: {username}")
            return None
        
        if not verify_password(password, user. hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        logger.info(f"User authenticated: {username}")
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args: 
            username: Username to look up
        
        Returns: 
            User if found, None otherwise
        """
        user_in_db = self.users.get(username)
        
        if not user_in_db: 
            return None
        
        return User(
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            created_at=user_in_db.created_at,
            is_active=user_in_db.is_active
        )
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        username = self.email_index.get(email)
        if username:
            return self.get_user(username)
        return None
    
    def create_access_token(self, username: str) -> str:
        """
        Create JWT access token for user
        
        Args: 
            username: Username to create token for
        
        Returns:
            JWT token string
        """
        return create_token(data={"sub": username})
    
    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate JWT token and return user
        
        Args:
            token: JWT token string
        
        Returns:
            User if token valid, None otherwise
        """
        payload = verify_token(token)
        
        if not payload: 
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        return self.get_user(username)
    
    def user_exists(self, username: str) -> bool:
        """Check if username exists"""
        return username in self.users
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        return email in self.email_index


# Global auth service instance
auth_service = AuthService()