"""
Database models for Gym Manager
PostgreSQL schema using SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='admin')
    market = Column(String(50), default='US', nullable=True)  # 'US' or 'PK' or 'VIP'
    subscription_expiry = Column(DateTime, nullable=True)  # Subscription expiry date
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gyms = relationship('Gym', back_populates='user', cascade='all, delete-orphan')

class Gym(Base):
    __tablename__ = 'gyms'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    logo_url = Column(String(500))
    currency = Column(String(10), default='Rs')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='gyms')
    members = relationship('Member', back_populates='gym', cascade='all, delete-orphan')
    expenses = relationship('Expense', back_populates='gym', cascade='all, delete-orphan')

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255))
    photo_url = Column(String(500))
    membership_type = Column(String(50), default='monthly')
    joined_date = Column(Date, default=datetime.utcnow().date)
    is_active = Column(Boolean, default=True, index=True)  # Changed from 'active' to 'is_active'
    is_trial = Column(Boolean, default=False)
    trial_end_date = Column(Date)
    birthday = Column(Date)  # For birthday alerts
    last_check_in = Column(DateTime)  # For inactive member tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gym = relationship('Gym', back_populates='members')
    fees = relationship('Fee', back_populates='member', cascade='all, delete-orphan')
    attendance = relationship('Attendance', back_populates='member', cascade='all, delete-orphan')
    notes = relationship('MemberNote', back_populates='member', cascade='all, delete-orphan')
    measurements = relationship('BodyMeasurement', back_populates='member', cascade='all, delete-orphan')

class Fee(Base):
    __tablename__ = 'fees'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False, index=True)  # INDEXED
    month = Column(String(7), nullable=False, index=True)  # INDEXED for monthly queries
    amount = Column(DECIMAL(10, 2), nullable=False)
    paid_date = Column(DateTime, nullable=False, index=True)  # INDEXED for date range queries
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    member = relationship('Member', back_populates='fees')

class Attendance(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    # check_in_time column removed - database doesn't have it, using created_at instead
    emotion = Column(String(50))
    confidence = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    member = relationship('Member', back_populates='attendance')

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gym = relationship('Gym', back_populates='expenses')

class MemberNote(Base):
    __tablename__ = 'member_notes'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    member = relationship('Member', back_populates='notes')

class BodyMeasurement(Base):
    __tablename__ = 'body_measurements'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    weight = Column(DECIMAL(5, 2))  # kg
    body_fat = Column(DECIMAL(5, 2))  # percentage
    chest = Column(DECIMAL(5, 2))  # cm
    waist = Column(DECIMAL(5, 2))  # cm
    arms = Column(DECIMAL(5, 2))  # cm
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    member = relationship('Member', back_populates='measurements')

# Database connection helper
def get_database_url():
    """Get database URL from environment or use local SQLite for development"""
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        # Railway/Render provides postgres:// but SQLAlchemy needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    else:
        # Local development - use SQLite
        return 'sqlite:///gym_manager.db'

def init_db():
    """Initialize database and create all tables"""
    url = get_database_url()
    try:
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        return engine
    except Exception as e:
        # Safe debug print (mask password)
        safe_url = url
        if '@' in safe_url:
            part1 = safe_url.split('@')[0]
            part2 = safe_url.split('@')[1]
            # Mask password
            if ':' in part1:
                safe_url = part1.split(':')[0] + ':****@' + part2
        
        print(f"❌ DB CONNECTION ERROR: {str(e)}")
        print(f"❌ URL Structure causing error: {safe_url}")
        raise e

def get_session():
    """Get database session with error handling"""
    try:
        engine = create_engine(get_database_url(), pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None
