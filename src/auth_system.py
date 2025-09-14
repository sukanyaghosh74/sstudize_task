"""
Production-ready user authentication system
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import sqlite3
import json
import logging
from dataclasses import dataclass
from enum import Enum
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    ADMIN = "admin"

class AuthStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    status: AuthStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    profile_data: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None

class AuthenticationSystem:
    """Production-ready authentication system with JWT tokens"""
    
    def __init__(self, db_path: str = "data/auth.db", secret_key: str = None):
        self.db_path = db_path
        self.secret_key = secret_key or self._generate_secret_key()
        self.token_expiry_hours = 24
        self._init_database()
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key for JWT signing"""
        return secrets.token_urlsafe(32)
    
    def _init_database(self):
        """Initialize authentication database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                profile_data TEXT,
                permissions TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Password reset tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            admin_user = self.get_user_by_username("admin")
            if not admin_user:
                self.register_user(
                    username="admin",
                    email="admin@roadmap-system.com",
                    password="admin123",  # Should be changed in production
                    role=UserRole.ADMIN,
                    profile_data={"full_name": "System Administrator"}
                )
                logger.info("Default admin user created")
        except Exception as e:
            logger.error(f"Error creating default admin: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except:
            return False
    
    def register_user(self, username: str, email: str, password: str, 
                     role: UserRole, profile_data: Optional[Dict] = None) -> bool:
        """Register a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_username(username) or self.get_user_by_email(email):
                logger.warning(f"User {username} or email {email} already exists")
                return False
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user_id = secrets.token_urlsafe(16)
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                status=AuthStatus.ACTIVE,
                created_at=datetime.now(),
                profile_data=profile_data or {},
                permissions=self._get_default_permissions(role)
            )
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, role, 
                                 status, created_at, profile_data, permissions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id,
                user.username,
                user.email,
                password_hash,
                user.role.value,
                user.status.value,
                user.created_at.isoformat(),
                json.dumps(user.profile_data),
                json.dumps(user.permissions)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User {username} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering user {username}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, email, password_hash, role, status,
                       created_at, last_login, profile_data, permissions
                FROM users WHERE username = ? AND status = 'active'
            ''', (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            # Verify password
            if not self.verify_password(password, row[3]):
                return None
            
            # Create user object
            user = User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                role=UserRole(row[4]),
                status=AuthStatus(row[5]),
                created_at=datetime.fromisoformat(row[6]),
                last_login=datetime.fromisoformat(row[7]) if row[7] else None,
                profile_data=json.loads(row[8]) if row[8] else {},
                permissions=json.loads(row[9]) if row[9] else []
            )
            
            # Update last login
            self._update_last_login(user.user_id)
            
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def create_session(self, user: User) -> str:
        """Create a new session for user"""
        try:
            session_id = secrets.token_urlsafe(32)
            token = self._generate_jwt_token(user)
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, token, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                user.user_id,
                token,
                datetime.now().isoformat(),
                expires_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session for user {user.user_id}: {e}")
            return None
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.token, s.expires_at, u.username, u.email, u.role,
                       u.status, u.created_at, u.last_login, u.profile_data, u.permissions
                FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.session_id = ? AND s.is_active = 1 AND s.expires_at > ?
            ''', (session_id, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            # Verify JWT token
            try:
                payload = jwt.decode(row[1], self.secret_key, algorithms=['HS256'])
                if payload['user_id'] != row[0]:
                    return None
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None
            
            # Create user object
            user = User(
                user_id=row[0],
                username=row[3],
                email=row[4],
                role=UserRole(row[5]),
                status=AuthStatus(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                last_login=datetime.fromisoformat(row[8]) if row[8] else None,
                profile_data=json.loads(row[9]) if row[9] else {},
                permissions=json.loads(row[10]) if row[10] else []
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error validating session {session_id}: {e}")
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by deactivating session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging out session {session_id}: {e}")
            return False
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _update_last_login(self, user_id: str):
        """Update user's last login time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, email, role, status, created_at,
                       last_login, profile_data, permissions
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                role=UserRole(row[3]),
                status=AuthStatus(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                profile_data=json.loads(row[7]) if row[7] else {},
                permissions=json.loads(row[8]) if row[8] else []
            )
            
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, email, role, status, created_at,
                       last_login, profile_data, permissions
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                role=UserRole(row[3]),
                status=AuthStatus(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                profile_data=json.loads(row[7]) if row[7] else {},
                permissions=json.loads(row[8]) if row[8] else []
            )
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def _get_default_permissions(self, role: UserRole) -> List[str]:
        """Get default permissions for user role"""
        permissions = {
            UserRole.STUDENT: [
                "view_own_profile",
                "view_own_roadmap",
                "update_own_profile",
                "submit_feedback"
            ],
            UserRole.TEACHER: [
                "view_students",
                "view_roadmaps",
                "create_roadmaps",
                "review_roadmaps",
                "submit_feedback",
                "view_reports"
            ],
            UserRole.PARENT: [
                "view_child_progress",
                "submit_observations",
                "view_reports",
                "submit_feedback"
            ],
            UserRole.ADMIN: [
                "manage_users",
                "manage_system",
                "view_all_data",
                "manage_permissions"
            ]
        }
        
        return permissions.get(role, [])
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current password hash
            cursor.execute('SELECT password_hash FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, row[0]):
                return False
            
            # Update password
            new_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE user_id = ?
            ''', (new_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None
            
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)  # 1 hour expiry
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (token, user.user_id, datetime.now().isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return token
            
        except Exception as e:
            logger.error(f"Error creating password reset token for {email}: {e}")
            return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get token info
            cursor.execute('''
                SELECT user_id, expires_at, used FROM password_reset_tokens
                WHERE token = ? AND used = 0 AND expires_at > ?
            ''', (token, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            user_id = row[0]
            
            # Update password
            new_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE user_id = ?
            ''', (new_hash, user_id))
            
            # Mark token as used
            cursor.execute('''
                UPDATE password_reset_tokens SET used = 1 WHERE token = ?
            ''', (token,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting password with token {token}: {e}")
            return False

class StreamlitAuthManager:
    """Streamlit-specific authentication manager"""
    
    def __init__(self, auth_system: AuthenticationSystem):
        self.auth_system = auth_system
    
    def login_form(self) -> Optional[User]:
        """Display login form and return authenticated user"""
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user = self.auth_system.authenticate_user(username, password)
                    if user:
                        # Store session in Streamlit session state
                        session_id = self.auth_system.create_session(user)
                        if session_id:
                            st.session_state['session_id'] = session_id
                            st.session_state['user'] = user
                            st.success(f"Welcome back, {user.username}!")
                            return user
                        else:
                            st.error("Failed to create session")
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        return None
    
    def register_form(self) -> bool:
        """Display registration form"""
        st.subheader("📝 Register")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", [role.value for role in UserRole])
            submit = st.form_submit_button("Register")
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                    return False
                
                success = self.auth_system.register_user(
                    username=username,
                    email=email,
                    password=password,
                    role=UserRole(role),
                    profile_data={"full_name": username}
                )
                
                if success:
                    st.success("Registration successful! Please login.")
                    return True
                else:
                    st.error("Registration failed. Username or email may already exist.")
                    return False
        
        return False
    
    def get_current_user(self) -> Optional[User]:
        """Get current logged-in user"""
        if 'session_id' in st.session_state and 'user' in st.session_state:
            # Validate session
            user = self.auth_system.validate_session(st.session_state['session_id'])
            if user:
                return user
            else:
                # Session expired or invalid
                self.logout()
                return None
        return None
    
    def logout(self):
        """Logout current user"""
        if 'session_id' in st.session_state:
            self.auth_system.logout_user(st.session_state['session_id'])
            del st.session_state['session_id']
        if 'user' in st.session_state:
            del st.session_state['user']
        st.rerun()
    
    def require_auth(self, required_roles: List[UserRole] = None):
        """Decorator to require authentication for a function"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                user = self.get_current_user()
                if not user:
                    st.error("Please login to access this page")
                    self.login_form()
                    return
                
                if required_roles and user.role not in required_roles:
                    st.error(f"Access denied. Required roles: {[r.value for r in required_roles]}")
                    return
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
