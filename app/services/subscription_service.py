"""Subscription service for managing user subscriptions"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.subscription import Subscription
from app.models.user import User
from app.utils.enums import SubscriptionType, PaymentStatus
from app.core.logging import logger


class SubscriptionService:
    """Service for subscription management"""
    
    # Subscription pricing (in rubles)
    SUBSCRIPTION_PRICES = {
        SubscriptionType.PREMIUM: {
            1: 299,   # 1 month
            3: 799,   # 3 months (10% discount)
            12: 2990  # 12 months (15% discount)
        },
        SubscriptionType.VIP: {
            1: 599,   # 1 month
            3: 1599,  # 3 months (10% discount)
            12: 5990  # 12 months (15% discount)
        }
    }
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get user's current subscription"""
        try:
            result = await self.session.execute(
                select(Subscription)
                .where(Subscription.user_id == user_id)
                .where(Subscription.is_active == True)
                .options(selectinload(Subscription.user))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return None
    
    async def create_subscription(
        self,
        user_id: int,
        subscription_type: SubscriptionType,
        duration_months: int,
        payment_method: str = "unknown",
        external_payment_id: Optional[str] = None
    ) -> Optional[Subscription]:
        """Create new subscription"""
        try:
            # Get price
            price = self.SUBSCRIPTION_PRICES.get(subscription_type, {}).get(duration_months)
            if not price:
                logger.error(f"Invalid subscription configuration: {subscription_type}, {duration_months} months")
                return None
            
            # Calculate dates
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_months * 30)
            
            # Check if user already has active subscription
            existing = await self.get_user_subscription(user_id)
            if existing:
                # Deactivate existing subscription
                existing.is_active = False
                existing.updated_at = datetime.utcnow()
            
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                start_date=start_date,
                end_date=end_date,
                price=price,
                payment_method=payment_method,
                external_payment_id=external_payment_id,
                payment_status=PaymentStatus.PENDING,
                is_active=False  # Will be activated after payment confirmation
            )
            
            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)
            
            logger.info(f"Subscription created for user {user_id}: {subscription_type} for {duration_months} months")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            await self.session.rollback()
            return None
    
    async def activate_subscription(
        self,
        subscription_id: int,
        payment_confirmation: Dict[str, Any]
    ) -> bool:
        """Activate subscription after successful payment"""
        try:
            # Get subscription
            result = await self.session.execute(
                select(Subscription)
                .where(Subscription.id == subscription_id)
                .options(selectinload(Subscription.user))
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                return False
            
            # Update subscription
            subscription.payment_status = PaymentStatus.COMPLETED
            subscription.is_active = True
            subscription.payment_confirmation = payment_confirmation
            subscription.updated_at = datetime.utcnow()
            
            # Update user subscription type
            user = subscription.user
            user.subscription_type = subscription.subscription_type
            user.updated_at = datetime.utcnow()
            
            await self.session.commit()
            
            logger.info(f"Subscription {subscription_id} activated for user {subscription.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating subscription: {e}")
            await self.session.rollback()
            return False
    
    async def cancel_subscription(
        self,
        user_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel user's subscription"""
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return False
            
            # Mark as cancelled but keep active until end date
            subscription.cancelled_at = datetime.utcnow()
            subscription.cancellation_reason = reason
            subscription.auto_renew = False
            subscription.updated_at = datetime.utcnow()
            
            await self.session.commit()
            
            logger.info(f"Subscription cancelled for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            await self.session.rollback()
            return False
    
    async def extend_subscription(
        self,
        user_id: int,
        additional_months: int
    ) -> bool:
        """Extend existing subscription"""
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return False
            
            # Extend end date
            subscription.end_date += timedelta(days=additional_months * 30)
            subscription.updated_at = datetime.utcnow()
            
            await self.session.commit()
            
            logger.info(f"Subscription extended for user {user_id} by {additional_months} months")
            return True
            
        except Exception as e:
            logger.error(f"Error extending subscription: {e}")
            await self.session.rollback()
            return False
    
    async def check_subscription_expiry(self) -> None:
        """Check and update expired subscriptions"""
        try:
            now = datetime.utcnow()
            
            # Find expired subscriptions
            result = await self.session.execute(
                select(Subscription)
                .where(
                    Subscription.is_active == True,
                    Subscription.end_date <= now
                )
                .options(selectinload(Subscription.user))
            )
            
            expired_subscriptions = result.scalars().all()
            
            for subscription in expired_subscriptions:
                # Deactivate subscription
                subscription.is_active = False
                subscription.updated_at = now
                
                # Downgrade user to free
                user = subscription.user
                user.subscription_type = SubscriptionType.FREE
                user.updated_at = now
                
                logger.info(f"Subscription expired for user {user.id}")
            
            if expired_subscriptions:
                await self.session.commit()
                logger.info(f"Processed {len(expired_subscriptions)} expired subscriptions")
            
        except Exception as e:
            logger.error(f"Error checking subscription expiry: {e}")
            await self.session.rollback()
    
    async def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        try:
            # Active subscriptions by type
            result = await self.session.execute(
                select(Subscription)
                .where(Subscription.is_active == True)
            )
            active_subscriptions = result.scalars().all()
            
            stats = {
                'total_active': len(active_subscriptions),
                'by_type': {},
                'total_revenue': 0,
                'avg_duration': 0
            }
            
            if not active_subscriptions:
                return stats
            
            # Group by type
            type_counts = {}
            total_revenue = 0
            total_duration = 0
            
            for sub in active_subscriptions:
                sub_type = sub.subscription_type
                type_counts[sub_type] = type_counts.get(sub_type, 0) + 1
                total_revenue += sub.price or 0
                
                # Calculate duration in days
                duration = (sub.end_date - sub.start_date).days
                total_duration += duration
            
            stats['by_type'] = {
                str(sub_type): count for sub_type, count in type_counts.items()
            }
            stats['total_revenue'] = total_revenue
            stats['avg_duration'] = total_duration / len(active_subscriptions) if active_subscriptions else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting subscription stats: {e}")
            return {}
    
    async def create_trial_subscription(self, user_id: int) -> Optional[Subscription]:
        """Create trial subscription for new users"""
        try:
            # Check if user already had a trial
            result = await self.session.execute(
                select(Subscription)
                .where(
                    Subscription.user_id == user_id,
                    Subscription.subscription_type == SubscriptionType.PREMIUM,
                    Subscription.price == 0  # Trial subscriptions have 0 price
                )
            )
            
            existing_trial = result.scalar_one_or_none()
            if existing_trial:
                logger.warning(f"User {user_id} already had a trial subscription")
                return None
            
            # Create 7-day trial
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)
            
            trial = Subscription(
                user_id=user_id,
                subscription_type=SubscriptionType.PREMIUM,
                start_date=start_date,
                end_date=end_date,
                price=0,  # Free trial
                payment_method="trial",
                payment_status=PaymentStatus.COMPLETED,
                is_active=True,
                is_trial=True
            )
            
            self.session.add(trial)
            
            # Update user subscription type
            await self.session.execute(
                update(User)
                .where(User.id == user_id)
                .values(subscription_type=SubscriptionType.PREMIUM)
            )
            
            await self.session.commit()
            await self.session.refresh(trial)
            
            logger.info(f"Trial subscription created for user {user_id}")
            return trial
            
        except Exception as e:
            logger.error(f"Error creating trial subscription: {e}")
            await self.session.rollback()
            return None
    
    def get_price(
        self,
        subscription_type: SubscriptionType,
        duration_months: int
    ) -> Optional[int]:
        """Get price for subscription type and duration"""
        return self.SUBSCRIPTION_PRICES.get(subscription_type, {}).get(duration_months)
    
    def get_all_plans(self) -> Dict[str, Any]:
        """Get all available subscription plans"""
        return {
            'premium': {
                'name': 'Premium',
                'description': 'Расширенные возможности анализа',
                'features': [
                    'До 9 анализов текста в день',
                    'До 5 профилей партнеров',
                    'Продвинутые тесты совместимости',
                    'Экспорт результатов',
                    'Приоритетная поддержка'
                ],
                'prices': self.SUBSCRIPTION_PRICES[SubscriptionType.PREMIUM]
            },
            'vip': {
                'name': 'VIP',
                'description': 'Безлимитные возможности + ИИ-коуч',
                'features': [
                    'Неограниченные анализы',
                    'До 20 профилей партнеров',
                    'Персональный ИИ-коуч',
                    'Детальные отчеты',
                    'Мгновенная поддержка',
                    'Эксклюзивный контент'
                ],
                'prices': self.SUBSCRIPTION_PRICES[SubscriptionType.VIP]
            }
        } 