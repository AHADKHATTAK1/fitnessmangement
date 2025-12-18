#!/usr/bin/env python
"""
Railway-optimized startup script
Handles environment setup and database initialization
"""

import os
import sys

def setup_environment():
    """Setup environment variables with fallbacks"""
    # Set default secret key if not provided
    if not os.getenv('FLASK_SECRET_KEY'):
        print("⚠️  FLASK_SECRET_KEY not set, using generated key")
        import secrets
        os.environ['FLASK_SECRET_KEY'] = secrets.token_hex(32)
    
    # Verify DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not set!")
        sys.exit(1)
    
    print("✅ Environment configured")

def initialize_database():
    """Initialize database tables"""
    try:
        from models import init_db
        print("🔄 Initializing database...")
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    print("🚀 Starting Railway deployment...")
    setup_environment()
    initialize_database()
    print("✅ Startup complete!")

if __name__ == '__main__':
    main()
