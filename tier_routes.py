"""
Subscription tier upgrade/downgrade routes
Handles Stripe checkout for tier changes
"""

from flask import request, redirect, url_for, session, flash
from subscription_tiers import TierManager, TIERS
from models import User
import stripe
import os
from datetime import datetime, timedelta

def init_upgrade_routes(app, auth_manager):
    """Initialize tier upgrade routes"""
    
    @app.route('/upgrade_tier', methods=['POST'])
    def upgrade_tier():
        """Handle tier upgrade with Stripe checkout"""
        username = session.get('username')
        if not username:
            flash('Please login first', 'error')
            return redirect(url_for('auth'))
        
        user = auth_manager.session.query(User).filter_by(email=username).first()
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth'))
        
        # Get form data
        new_tier = request.form.get('tier')
        billing_cycle = request.form.get('cycle', 'monthly')
        
        # Validate tier
        if new_tier not in TIERS:
            flash('Invalid tier selected', 'error')
            return redirect(url_for('subscription_plans'))
        
        # Get tier config
        tier_config = TIERS[new_tier]
        
        # Calculate amount
        if billing_cycle == 'yearly':
            amount = tier_config['price_yearly']
            interval = 'year'
        else:
            amount = tier_config['price_monthly']
            interval = 'month'
        
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{tier_config["name"]} Plan',
                            'description': f'{tier_config["description"]}',
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                        'recurring': {
                            'interval': interval
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('upgrade_success', tier=new_tier, cycle=billing_cycle, _external=True),
                cancel_url=url_for('subscription_plans', _external=True),
                client_reference_id=user.email,
                metadata={
                    'tier': new_tier,
                    'billing_cycle': billing_cycle,
                    'user_email': user.email
                }
            )
            
            return redirect(checkout_session.url)
            
        except Exception as e:
            flash(f'Payment error: {str(e)}', 'error')
            return redirect(url_for('subscription_plans'))
    
    
    @app.route('/upgrade_success')
    def upgrade_success():
        """Handle successful tier upgrade"""
        username = session.get('username')
        if not username:
            return redirect(url_for('auth'))
        
        user = auth_manager.session.query(User).filter_by(email=username).first()
        if not user:
            return redirect(url_for('auth'))
        
        # Get tier and cycle from query params
        new_tier = request.args.get('tier')
        billing_cycle = request.args.get('cycle', 'monthly')
        
        # Update user subscription
        user.subscription_tier = new_tier
        user.billing_cycle = billing_cycle
        user.tier_upgraded_at = datetime.utcnow()
        
        # Set new expiry date
        if billing_cycle == 'yearly':
            user.subscription_expiry = datetime.utcnow() + timedelta(days=365)
        else:
            user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
        
        user.subscription_status = 'active'
        
        auth_manager.session.commit()
        
        # Send confirmation email (if email_utils available)
        try:
            from email_utils import send_email
            tier_config = TIERS[new_tier]
            send_email(
                to=user.email,
                subject=f'🎉 Subscription Upgraded to {tier_config["name"]}!',
                body=f'''
                Congratulations!
                
                Your subscription has been upgraded to {tier_config["name"]} plan.
                
                Plan Details:
                - Members: {tier_config["limits"]["members"] if tier_config["limits"]["members"] != -1 else "Unlimited"}
                - Gyms: {tier_config["limits"]["gyms"] if tier_config["limits"]["gyms"] != -1 else "Unlimited"}
                - Billing: {billing_cycle}
                
                Thank you for your business!
                '''
            )
        except:
            pass  # Email optional
        
        flash(f'🎉 Successfully upgraded to {TIERS[new_tier]["name"]} plan!', 'success')
        return redirect(url_for('dashboard'))
    
    
    @app.route('/downgrade_tier', methods=['POST'])
    def downgrade_tier():
        """Schedule tier downgrade (applies at end of billing cycle)"""
        username = session.get('username')
        if not username:
            return redirect(url_for('auth'))
        
        user = auth_manager.session.query(User).filter_by(email=username).first()
        if not user:
            return redirect(url_for('auth'))
        
        new_tier = request.form.get('tier')
        
        # Can't downgrade to a higher tier
        tier_order = ['starter', 'professional', 'enterprise', 'enterprise_plus']
        current_idx = tier_order.index(user.subscription_tier)
        new_idx = tier_order.index(new_tier)
        
        if new_idx >= current_idx:
            flash('That is not a downgrade', 'error')
            return redirect(url_for('subscription_plans'))
        
        # Schedule downgrade
        user.tier_downgrade_scheduled = new_tier
        auth_manager.session.commit()
        
        flash(f'Downgrade scheduled. Will switch to {TIERS[new_tier]["name"]} at end of billing cycle.', 'info')
        return redirect(url_for('subscription_plans'))
    
    
    @app.route('/cancel_subscription', methods=['POST'])
    def cancel_subscription():
        """Cancel subscription (switch to starter at end of period)"""
        username = session.get('username')
        if not username:
            return redirect(url_for('auth'))
        
        user = auth_manager.session.query(User).filter_by(email=username).first()
        if not user:
            return redirect(url_for('auth'))
        
        # Schedule downgrade to starter
        user.tier_downgrade_scheduled = 'starter'
        auth_manager.session.commit()
        
        flash('Subscription will be canceled at end of billing period. You will be moved to Starter plan.', 'info')
        return redirect(url_for('settings'))
