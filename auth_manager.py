"""
Database-backed Authentication Manager
Uses PostgreSQL User table instead of JSON files
"""

from models import User, get_session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import os
import json

class AuthManager:
    def __init__(self):
        self.session = get_session()
        if not self.session:
            print("⚠️ Running in LEGACY JSON MODE (DB connection failed)")
            self.legacy = True
            # Load users from JSON as fallback
            self.users_file = 'users.json'
            self.users = self.load_users()
        else:
            self.legacy = False
            self.users = {} # Prevent AttributeError in context processors
            print("✅ Running in DATABASE MODE")

    def load_users(self):
        if os.path.exists('users.json'):
            try:
                with open('users.json', 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def hash_password(self, password):
        """Hash password using werkzeug"""
        return generate_password_hash(password)
    
    def check_password(self, password_hash, password):
        """Verify password"""
        return check_password_hash(password_hash, password)
    
    def user_exists(self, username):
        """Check if user exists"""
        if self.legacy:
            return username in self.users
            
        user = self.session.query(User).filter_by(email=username).first()
        return user is not None
    
    def validate_referral(self, code):
        """Check if referral code is valid"""
        valid_codes = ['VIP2025', 'FREE']
        return code and code.upper() in valid_codes
    
    def create_user(self, username, password, referral_code=None):
        """Create a new user"""
        if self.legacy:
            if username in self.users: return False
            self.users[username] = {
                'password': self.hash_password(password),
                'role': 'admin',
                'joined_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open('users.json', 'w') as f:
                json.dump(self.users, f)
            return True

        if self.user_exists(username):
            return False
        
        user = User(
            email=username,
            password_hash=self.hash_password(password),
            role='admin'
        )
        
        self.session.add(user)
        self.session.commit()
        return True
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        if self.legacy:
            if username not in self.users: return False
            stored_hash = self.users[username].get('password')
            if stored_hash.startswith('scrypt:') or stored_hash.startswith('pbkdf2:'):
                return check_password_hash(stored_hash, password)
            import hashlib
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            return stored_hash == sha256_hash

        user = self.session.query(User).filter_by(email=username).first()
        if not user:
            return False
        
        # Try Werkzeug hash first (new format)
        if user.password_hash.startswith('scrypt:') or user.password_hash.startswith('pbkdf2:'):
            return self.check_password(user.password_hash, password)
        else:
            # Old SHA256 format - check directly
            import hashlib
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == sha256_hash:
                # Update to new format for future logins
                user.password_hash = self.hash_password(password)
                self.session.commit()
                return True
            return False
    
    def get_user_data_file(self, username):
        """Get user's data file path (legacy - not used with PostgreSQL)"""
        return f"gym_data/{username}.json"
    
    def is_subscription_active(self, username):
        """Check if user's subscription is active"""
        # For now, all users are active. Can add logic later.
        return True

    # Password Reset Methods
    def generate_reset_code(self, username):
        """Generate a 6-digit reset code"""
        if self.legacy:
            if username not in self.users: return None
            return str(secrets.randbelow(900000) + 100000)

        user = self.session.query(User).filter_by(email=username).first()
        if not user:
            return None
        
        code = str(secrets.randbelow(900000) + 100000)  # 6-digit code
        return code
    
    def verify_reset_code(self, username, code):
        """Verify reset code (simplified for now)"""
        return True  # Simplified
    
    def update_password(self, username, new_password):
        """Update user password"""
        if self.legacy:
            if username not in self.users: return False
            self.users[username]['password'] = self.hash_password(new_password)
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f)
            return True

        user = self.session.query(User).filter_by(email=username).first()
        if not user:
            return False
        
        user.password_hash = self.hash_password(new_password)
        self.session.commit()
        return True
    
    def __del__(self):
        """Close database session"""
        if hasattr(self, 'session'):
            self.session.close()
