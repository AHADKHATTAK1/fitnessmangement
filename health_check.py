"""
Railway deployment health check and error logging
"""

from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    checks = {
        'status': 'ok',
        'database_url': 'set' if os.getenv('DATABASE_URL') else 'missing',
        'python_version': sys.version,
    }
    
    # Test database connection
    try:
        from models import get_session
        session = get_session()
        session.execute('SELECT 1')
        session.close()
        checks['database'] = 'connected'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        checks['status'] = 'error'
    
    return jsonify(checks)

if __name__ == '__main__':
    # Test imports
    print("Testing imports...")
    try:
        from models import init_db, User, Gym
        print("✅ Models imported")
        
        from auth_manager import AuthManager
        print("✅ AuthManager imported")
        
        from gym_manager import GymManager
        print("✅ GymManager imported")
        
        # Test database
        print("\nTesting database connection...")
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            print(f"✅ DATABASE_URL found")
            init_db()
            print("✅ Database initialized")
        else:
            print("❌ DATABASE_URL not set")
        
        print("\n✅ All checks passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
