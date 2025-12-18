"""
Simple Direct Migration - Bypass GymManager
Directly reads JSON and writes to PostgreSQL
"""
import json
import os
from datetime import datetime
from models import init_db, get_session, User, Gym, Member, Fee

def main():
    print("🚀 Starting DIRECT migration to new Railway database...")
    
    # Initialize database
    init_db()
    session = get_session()
    
    if not session:
        print("❌ Failed to connect to database!")
        return
    
    # Check current data count
    existing_users = session.query(User).count()
    existing_members = session.query(Member).count()
    
    print(f"📊 Current database state:")
    print(f"   Users: {existing_users}")
    print(f"   Members: {existing_members}")
    
    if existing_members > 0:
        response = input(f"\n⚠️  Database already has {existing_members} members. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return
    
    # Migrate users
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        for email, data in users_data.items():
            user = session.query(User).filter_by(email=email).first()
            if not user:
                print(f"✅ Creating user: {email}")
                user = User(
                    email=email,
                    password_hash=data.get('password'),
                    role='admin'
                )
                session.add(user)
        session.commit()
    
    # Migrate gym data
    gym_files = []
    if os.path.exists('gym_data'):
        gym_files = [f for f in os.listdir('gym_data') if f.endswith('.json')]
    
    print(f"\n📂 Found {len(gym_files)} gym data files")
    
    for filename in gym_files:
        email = filename.replace('.json', '')
        filepath = os.path.join('gym_data', filename)
        
        print(f"\n👤 Processing: {email}")
        
        # Get or create user
        user = session.query(User).filter_by(email=email).first()
        if not user:
            print(f"   Creating user: {email}")
            user = User(email=email, password_hash='temp', role='admin')
            session.add(user)
            session.commit()
        
        # Load gym data
        with open(filepath, 'r', encoding='utf-8') as f:
            gym_data = json.load(f)
        
        # Create gym
        gym = session.query(Gym).filter_by(user_id=user.id).first()
        if not gym:
            gym_details = gym_data.get('gym_details', {})
            gym = Gym(
                user_id=user.id,
                name=gym_details.get('name', 'Gym Manager'),
                currency=gym_details.get('currency', 'Rs')
            )
            session.add(gym)
            session.commit()
        
        # Migrate members
        members_data = gym_data.get('members', {})
        member_mapping = {}
        member_count = 0
        
        for json_id, m_data in members_data.items():
            # Check if already exists by phone
            existing = session.query(Member).filter_by(
                gym_id=gym.id, 
                phone=m_data.get('phone')
            ).first()
            
            if existing:
                member_mapping[json_id] = existing.id
                continue
            
            try:
                joined = datetime.strptime(m_data.get('joined'), '%Y-%m-%d').date()
            except:
                joined = datetime.now().date()
            
            member = Member(
                gym_id=gym.id,
                name=m_data.get('name'),
                phone=m_data.get('phone'),
                membership_type=m_data.get('membership_type'),
                joined_date=joined,
                is_active=True
            )
            session.add(member)
            session.flush()
            member_mapping[json_id] = member.id
            member_count += 1
        
        session.commit()
        print(f"   ✅ Migrated {member_count} members")
        
        # Migrate fees
        fees_data = gym_data.get('fees', {})
        fee_count = 0
        
        for json_id, months in fees_data.items():
            db_id = member_mapping.get(json_id)
            if not db_id:
                continue
            
            for month, fee_info in months.items():
                # Check if fee already exists
                existing = session.query(Fee).filter_by(
                    member_id=db_id,
                    month=month
                ).first()
                
                if existing:
                    continue
                
                try:
                    date_str = fee_info.get('date') or fee_info.get('timestamp')
                    if date_str:
                        paid_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        paid_date = datetime.now()
                except:
                    paid_date = datetime.now()
                
                fee = Fee(
                    member_id=db_id,
                    month=month,
                    amount=fee_info.get('amount', 0),
                    paid_date=paid_date
                )
                session.add(fee)
                fee_count += 1
        
        session.commit()
        print(f"   ✅ Migrated {fee_count} fee records")
    
    # Final count
    total_users = session.query(User).count()
    total_members = session.query(Member).count()
    total_fees = session.query(Fee).count()
    
    print(f"\n🎉 Migration Complete!")
    print(f"   Total Users: {total_users}")
    print(f"   Total Members: {total_members}")
    print(f"   Total Fees: {total_fees}")
    
    session.close()

if __name__ == "__main__":
    main()
