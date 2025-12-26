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
        valid_codes = ['500596AK1'] # New VIP Code
        return code and code in valid_codes
    
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
        
        # TEMPORARILY DISABLED - Run /fix_db first
        # # Determine trial/expiry based on code
        # if referral_code == '500596AK1':
        #     expiry = datetime(2099, 1, 1) # Lifetime Access
        #     market = 'VIP'
        # else:
        #     expiry = datetime.utcnow() + timedelta(days=30) # 30 Days Trial
        #     market = 'US' # Default

        user = User(
            email=username,
            password_hash=self.hash_password(password),
            role='admin'
            # TEMPORARILY DISABLED:
            # market=market,
            # subscription_expiry=expiry
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
        if not user: return False
        
        if user.password_hash.startswith('scrypt:') or user.password_hash.startswith('pbkdf2:'):
            return self.check_password(user.password_hash, password)
        else:
            # Legacy SHA256 check
            import hashlib
            if user.password_hash == hashlib.sha256(password.encode()).hexdigest():
                user.password_hash = self.hash_password(password)
                self.session.commit()
                return True
            return False

    def is_subscription_active(self, username):
        """Check if user's subscription is active (with 3-day grace period)"""
        user = self.session.query(User).filter_by(email=username).first()
        if not user:
            return False
        
        # VIP code (500596AK1) gets lifetime access
        if hasattr(user, 'market') and user.market == 'VIP':
            return True
        
        # Check expiry with 3-day grace period
        if user.subscription_expiry:
            grace_period = timedelta(days=3)
            return datetime.utcnow() < (user.subscription_expiry + grace_period)
        
        # If no expiry set, give 30 days trial from account creation
        if user.created_at:
            trial_end = user.created_at + timedelta(days=30)
            return datetime.utcnow() < trial_end
        
        return False

    def extend_subscription(self, username, days=30):
        """Extend user's subscription by specified days"""
        user = self.session.query(User).filter_by(email=username).first()
        if user:
            if not user.subscription_expiry:
                user.subscription_expiry = datetime.utcnow() + timedelta(days=days)
            else:
                user.subscription_expiry += timedelta(days=days)
            self.session.commit()
            return True
        return False
    
    def set_market(self, username, market):
        """Set user's market region ('US', 'PK', or 'VIP')"""
        user = self.session.query(User).filter_by(email=username).first()
        if user:
            user.market = market
            self.session.commit()
            return True
        return False
    
    def get_market(self, username):
        """TEMPORARILY DISABLED"""
        return 'US'  # Disabled until /fix_db is run
        # user = self.session.query(User).filter_by(email=username).first()
        # return user.market if user else 'US'

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
