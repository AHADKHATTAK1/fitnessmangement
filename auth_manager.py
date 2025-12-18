import json
import os
import hashlib
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        try:
            self.users = self.load_users()
            print(f"Loaded {len(self.users)} users from {users_file}")
        except Exception as e:
            print(f"Error loading users: {str(e)}")
            self.users = {}

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON decode error: {str(e)}")
                return {}
            except Exception as e:
                print(f"File read error: {str(e)}")
                return {}
        return {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def user_exists(self, username):
        return username in self.users

    def validate_referral(self, code):
        """Check if referral code is valid."""
        valid_codes = ['VIP2025', 'FREE']
        return code and code.upper() in valid_codes

    def create_user(self, username, password, referral_code=None):
        if username in self.users:
            return False
        
        if referral_code and self.validate_referral(referral_code):
            plan = 'free_lifetime'
            expiry = '2099-12-31'
        else:
            plan = 'standard'
            expiry = None
        
        self.users[username] = {
            'password': self.hash_password(password),
            'joined_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'referral_code': referral_code,
            'plan': plan,
            'plan_expiry': expiry
        }
        self.save_users()
        return True

    def verify_user(self, username, password):
        if username not in self.users:
            return False
        return self.users[username]['password'] == self.hash_password(password)

    def get_user_data_file(self, username):
        """Get the data file path for a user"""
        return f"gym_data/{username}.json"

    def is_subscription_active(self, username):
        """Check if user's subscription is active"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        plan = user.get('plan', 'standard')
        
        # Free lifetime plan is always active
        if plan == 'free_lifetime':
            return True
        
        # Check expiry date
        expiry = user.get('plan_expiry')
        if not expiry:
            return False
        
        try:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
            return datetime.now() <= expiry_date
        except:
            return False

    # Password Reset Methods
    def generate_reset_code(self, username):
        """Generate a 6-digit reset code"""
        if username not in self.users:
            return None
        
        import secrets
        code = str(secrets.randbelow(900000) + 100000)
        expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        
        self.users[username]['reset_code'] = code
        self.users[username]['reset_code_expiry'] = expiry
        self.save_users()
        
        return code

    def verify_reset_code(self, username, code):
        """Verify reset code"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        stored_code = user.get('reset_code')
        expiry = user.get('reset_code_expiry')
        
        if not stored_code or not expiry:
            return False
        
        # Check if code matches
        if stored_code != code:
            return False
        
        # Check if expired
        try:
            expiry_time = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
            if datetime.now() > expiry_time:
                return False
        except:
            return False
        
        return True

    def update_password(self, username, new_password):
        """Update user password"""
        if username not in self.users:
            return False
        
        self.users[username]['password'] = self.hash_password(new_password)
        # Clear reset code
        if 'reset_code' in self.users[username]:
            del self.users[username]['reset_code']
        if 'reset_code_expiry' in self.users[username]:
            del self.users[username]['reset_code_expiry']
        
        self.save_users()
        return True
