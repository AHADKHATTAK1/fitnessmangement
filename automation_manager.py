"""
Marketing Automation Manager
Handles automated campaigns: payment reminders, birthday wishes, re-engagement
"""

from datetime import datetime, timedelta
from typing import List, Dict
from models import Member, Fee, Gym
from email_sender import EmailSender
import os


class AutomationManager:
    """Intelligent marketing automation for member engagement"""
    
    def __init__(self, session, email_sender: EmailSender = None):
        self.session = session
        self.email_sender = email_sender or EmailSender()
    
    # ==================== PAYMENT REMINDERS ====================
    
    def check_payment_reminders(self, gym_id: int, days_before: int = 3) -> List[Dict]:
        """
        Find members who need payment reminders
        
        Args:
            gym_id: Gym ID to check
            days_before: Send reminder N days before month end
        
        Returns:
            List of members needing reminders
        """
        today = datetime.now().date()
        current_month = datetime.now().strftime('%Y-%m')
        
        # Calculate if we should send (e.g., 3 days before month end)
        days_left_in_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        days_remaining = (days_left_in_month.date() - today).days
        
        if days_remaining != days_before:
            return []  # Not time to send yet
        
        # Get unpaid members
        from sqlalchemy import and_
        
        unpaid_members = self.session.query(Member).filter(
            Member.gym_id == gym_id,
            Member.active == True
        ).all()
        
        reminders_to_send = []
        for member in unpaid_members:
            # Check if already paid this month
            paid_this_month = self.session.query(Fee).filter(
                Fee.member_id == member.id,
                Fee.month == current_month
            ).first()
            
            if not paid_this_month:
                reminders_to_send.append({
                    'member_id': member.id,
                    'name': member.name,
                    'email': member.email,
                    'phone': member.phone,
                    'month': current_month,
                    'amount_due': 5000  # Default, should come from membership type
                })
        
        return reminders_to_send
    
    def send_payment_reminder(self, member: Dict, gym: Gym) -> bool:
        """Send payment reminder email to member"""
        if not member.get('email'):
            return False
        
        subject = f"Payment Reminder - {gym.name}"
        
        # HTML email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">💳 Payment Reminder</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Hi <strong>{member['name']}</strong>,</p>
                
                <p>This is a friendly reminder that your membership payment for <strong>{member['month']}</strong> is due soon.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="margin-top: 0;">Payment Details:</h3>
                    <p><strong>Amount:</strong> {gym.currency}{member['amount_due']}</p>
                    <p><strong>Due Date:</strong> End of {member['month']}</p>
                </div>
                
                <p>Please make your payment at your earliest convenience to avoid any interruption in your membership.</p>
                
                <p style="margin-top: 30px;">Thank you for being a valued member!</p>
                
                <p>Best regards,<br>
                <strong>{gym.name}</strong></p>
            </div>
            
            <div style="background: #1f2937; color: white; padding: 20px; text-align: center; font-size: 12px;">
                <p>You received this email because you are a member at {gym.name}</p>
            </div>
        </body>
        </html>
        """
        
        return self.email_sender.send_email(member['email'], subject, body)
    
    # ==================== BIRTHDAY WISHES ====================
    
    def check_birthdays_today(self, gym_id: int) -> List[Dict]:
        """Find members with birthday today"""
        today = datetime.now().date()
        
        members = self.session.query(Member).filter(
            Member.gym_id == gym_id,
            Member.active == True,
            Member.birthday.isnot(None)
        ).all()
        
        birthday_members = []
        for member in members:
            if member.birthday and member.birthday.month == today.month and member.birthday.day == today.day:
                birthday_members.append({
                    'member_id': member.id,
                    'name': member.name,
                    'email': member.email,
                    'phone': member.phone,
                    'age': today.year - member.birthday.year
                })
        
        return birthday_members
    
    def send_birthday_wish(self, member: Dict, gym: Gym) -> bool:
        """Send birthday email"""
        if not member.get('email'):
            return False
        
        subject = f"🎉 Happy Birthday from {gym.name}!"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; font-size: 48px; margin: 0;">🎂</h1>
                <h1 style="color: white; margin: 10px 0;">Happy Birthday!</h1>
            </div>
            
            <div style="padding: 40px; background: #fff;">
                <p style="font-size: 18px;">Dear <strong>{member['name']}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    The entire team at {gym.name} wishes you a very happy birthday! 🎉
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Thank you for being such an amazing part of our fitness family. 
                    We hope your special day is filled with joy, health, and happiness!
                </p>
                
                <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #92400e; margin-top: 0;">🎁 Birthday Special!</h3>
                    <p style="color: #78350f; margin-bottom: 0;">Show this email for a special surprise at your next visit!</p>
                </div>
                
                <p style="margin-top: 30px; font-size: 16px;">
                    Keep crushing your fitness goals!
                </p>
                
                <p>With love,<br>
                <strong>Team {gym.name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return self.email_sender.send_email(member['email'], subject, body)
    
    # ==================== WELCOME SEQUENCE ====================
    
    def send_welcome_email(self, member_id: int) -> bool:
        """Send welcome email to new member"""
        member = self.session.query(Member).filter_by(id=member_id).first()
        if not member or not member.email:
            return False
        
        gym = self.session.query(Gym).filter_by(id=member.gym_id).first()
        
        subject = f"Welcome to {gym.name}! 🎉"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">Welcome Aboard!</h1>
            </div>
            
            <div style="padding: 40px; background: #fff;">
                <p style="font-size: 18px;">Hi <strong>{member.name}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Welcome to the {gym.name} family! We're thrilled to have you join us on your fitness journey. 💪
                </p>
                
                <h3>Here's what to expect:</h3>
                <ul style="line-height: 1.8;">
                    <li>✅ Access to all gym equipment and facilities</li>
                    <li>✅ Professional trainers to guide you</li>
                    <li>✅ Group classes and specialized programs</li>
                    <li>✅ Member portal for tracking your progress</li>
                </ul>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">🎯 Quick Start Tips:</h3>
                    <ol style="margin: 0; padding-left: 20px;">
                        <li>Download your membership card from the portal</li>
                        <li>Book your first free fitness assessment</li>
                        <li>Join our WhatsApp community for updates</li>
                        <li>Set your fitness goals in your profile</li>
                    </ol>
                </div>
                
                <p style="font-size: 16px; margin-top: 30px;">
                    If you have any questions, we're here to help!
                </p>
                
                <p>Best regards,<br>
                <strong>Team {gym.name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return self.email_sender.send_email(member.email, subject, body)
    
    # ==================== RE-ENGAGEMENT CAMPAIGNS ====================
    
    def check_inactive_members(self, gym_id: int, inactive_days: int = 30) -> List[Dict]:
        """Find members who haven't checked in recently"""
        cutoff_date = datetime.now() - timedelta(days=inactive_days)
        
        inactive_members = self.session.query(Member).filter(
            Member.gym_id == gym_id,
            Member.active == True,
            Member.last_check_in < cutoff_date
        ).all()
        
        return [{
            'member_id': m.id,
            'name': m.name,
            'email': m.email,
            'phone': m.phone,
            'last_visit': m.last_check_in.strftime('%Y-%m-%d') if m.last_check_in else 'Never'
        } for m in inactive_members if m.email]
    
    def send_comeback_email(self, member: Dict, gym: Gym) -> bool:
        """Send re-engagement email"""
        subject = f"We Miss You at {gym.name}! 💙"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">We Miss You!</h1>
            </div>
            
            <div style="padding: 40px; background: #fff;">
                <p style="font-size: 18px;">Hi <strong>{member['name']}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    We noticed you haven't visited {gym.name} in a while. 
                    Your last visit was on <strong>{member['last_visit']}</strong>.
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Life gets busy - we totally get it! But your fitness goals are waiting for you. 💪
                </p>
                
                <div style="background: #10b981; color: white; padding: 30px; border-radius: 8px; margin: 30px 0; text-align: center;">
                    <h2 style="margin-top: 0;">🎁 Comeback Special!</h2>
                    <p style="font-size: 20px; margin-bottom: 0;">
                        Get <strong>20% OFF</strong> your next month when you visit this week!
                    </p>
                </div>
                
                <p style="font-size: 16px;">
                    We'd love to see you back at the gym. Your community is here waiting for you!
                </p>
                
                <p style="margin-top: 30px;">Stay strong,<br>
                <strong>Team {gym.name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return self.email_sender.send_email(member['email'], subject, body)
    
    # ==================== BULK AUTOMATION RUNNER ====================
    
    def run_daily_automations(self, gym_id: int) -> Dict:
        """
        Run all daily automation checks
        Should be called by scheduler (cron job or Celery)
        """
        gym = self.session.query(Gym).filter_by(id=gym_id).first()
        results = {
            'payment_reminders': 0,
            'birthdays': 0,
            'reengagement': 0,
            'errors': []
        }
        
        try:
            # Payment Reminders
            payment_reminders = self.check_payment_reminders(gym_id, days_before=3)
            for member in payment_reminders:
                if self.send_payment_reminder(member, gym):
                    results['payment_reminders'] += 1
            
            # Birthday Wishes
            birthdays = self.check_birthdays_today(gym_id)
            for member in birthdays:
                if self.send_birthday_wish(member, gym):
                    results['birthdays'] += 1
            
            # Re-engagement (run weekly, check day of week)
            if datetime.now().weekday() == 0:  # Monday
                inactive = self.check_inactive_members(gym_id, inactive_days=30)
                for member in inactive[:10]:  # Limit to 10 per week
                    if self.send_comeback_email(member, gym):
                        results['reengagement'] += 1
        
        except Exception as e:
            results['errors'].append(str(e))
        
        return results
