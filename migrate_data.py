import json
import os
from datetime import datetime
from models import init_db, get_session, User, Gym, Member, Fee, Attendance, Expense
from auth_manager import AuthManager
from gym_manager import GymManager

def migrate():
    # Initialize DB (creates tables)
    init_db()
    session = get_session()
    auth = AuthManager()
    
    print("🚀 Starting migration...")
    
    # 1. Load users from users.json
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            users_data = json.load(f)
            
        for email, data in users_data.items():
            print(f"Migrating user: {email}")
            
            # Create user if doesn't exist
            user = session.query(User).filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    password_hash=data.get('password'), # Keep existing hash (AuthManager handles SHA256)
                    role='admin',
                    created_at=datetime.strptime(data.get('joined_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                )
                session.add(user)
                session.commit()
            
            # 2. Migrate gym data for this user
            user_data_file = f"gym_data/{email}.json"
            if os.path.exists(user_data_file):
                print(f"  Found data file: {user_data_file}")
                with open(user_data_file, 'r') as f:
                    gym_data = json.load(f)
                
                # Create Gym
                gym_details = gym_data.get('gym_details', {})
                gym = session.query(Gym).filter_by(user_id=user.id).first()
                if not gym:
                    gym = Gym(
                        user_id=user.id,
                        name=gym_details.get('name', 'Gym Manager'),
                        logo_url=gym_details.get('logo'),
                        currency=gym_details.get('currency', 'Rs')
                    )
                    session.add(gym)
                    session.commit()
                
                # Create Members
                members_data = gym_data.get('members', {})
                member_mapping = {} # json_id -> db_id
                
                for json_id, m in members_data.items():
                    # Parse joined date safely
                    try:
                        jd_str = m.get('joined_date')
                        if jd_str:
                            jd = datetime.strptime(jd_str, '%Y-%m-%d').date()
                        else:
                            jd = datetime.now().date()
                    except:
                        jd = datetime.now().date()
                        
                    member = Member(
                        gym_id=gym.id,
                        name=m.get('name'),
                        phone=m.get('phone'),
                        email=m.get('email'),
                        photo_url=m.get('photo'),
                        membership_type=m.get('membership_type', 'Gym'),
                        joined_date=jd,
                        is_active=m.get('active', True),
                        is_trial=m.get('is_trial', False),
                        trial_end_date=datetime.strptime(m.get('trial_end_date'), '%Y-%m-%d').date() if m.get('trial_end_date') else None
                    )
                    session.add(member)
                    session.commit()
                    member_mapping[json_id] = member.id
                
                print(f"  Migrated {len(member_mapping)} members")
                
                # Create Fees
                fees_data = gym_data.get('fees', {})
                fee_count = 0
                for json_mid, member_fees in fees_data.items():
                    db_mid = member_mapping.get(json_mid)
                    if not db_mid: continue
                    
                    for month, f_info in member_fees.items():
                        try:
                            pd_str = f_info.get('date')
                            if pd_str:
                                try:
                                    pd = datetime.strptime(pd_str, '%Y-%m-%d %H:%M:%S')
                                except:
                                    pd = datetime.strptime(pd_str, '%Y-%m-%d')
                            else:
                                pd = datetime.now()
                        except:
                            pd = datetime.now()
                            
                        fee = Fee(
                            member_id=db_mid,
                            month=month,
                            amount=f_info.get('amount', 0),
                            paid_date=pd
                        )
                        session.add(fee)
                        fee_count += 1
                session.commit()
                print(f"  Migrated {fee_count} fee records")
                
                # Create Expenses
                expenses_data = gym_data.get('expenses', [])
                for e in expenses_data:
                    try:
                        ed = datetime.strptime(e.get('date'), '%Y-%m-%d').date()
                    except:
                        ed = datetime.now().date()
                        
                    expense = Expense(
                        gym_id=gym.id,
                        category=e.get('category'),
                        amount=e.get('amount', 0),
                        date=ed,
                        description=e.get('description', '')
                    )
                    session.add(expense)
                session.commit()
                print(f"  Migrated {len(expenses_data)} expenses")
                
                # Create Attendance
                attendance_data = gym_data.get('attendance', {})
                att_count = 0
                for json_mid, records in attendance_data.items():
                    db_mid = member_mapping.get(json_mid)
                    if not db_mid: continue
                    
                    for r in records:
                        try:
                            ts = datetime.strptime(r.get('timestamp'), '%Y-%m-%d %H:%M:%S')
                        except:
                            ts = datetime.now()
                            
                        att = Attendance(
                            member_id=db_mid,
                            check_in_time=ts,
                            emotion=r.get('emotion'),
                            confidence=r.get('confidence')
                        )
                        session.add(att)
                        att_count += 1
                session.commit()
                print(f"  Migrated {att_count} attendance records")

    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
