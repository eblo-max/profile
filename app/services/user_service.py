"""User service for managing user data and operations"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.analytics import UserActivity, UserAchievement
from app.models.subscription import Subscription
from app.utils.enums import SubscriptionType, ActivityType
from app.core.logging import logger


class UserService:
    """Service for user management operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one"""
        try:
            # Try to get existing user
            result = await self.session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update user info if changed
                if (user.username != username or 
                    user.first_name != first_name or 
                    user.last_name != last_name):
                    
                    user.username = username
                    user.first_name = first_name
                    user.last_name = last_name
                    user.last_activity = datetime.utcnow()
                    
                    await self.session.commit()
                
                return user
            
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                subscription_type="FREE",
                is_new_user=True
            )
            
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            
            # Log user registration
            await self.log_activity(user.id, ActivityType.USER_REGISTERED)
            
            logger.info(f"New user created: {telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            await self.session.rollback()
            raise
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.telegram_id == telegram_id)
                .options(selectinload(User.subscriptions))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.subscriptions))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            return None
    
    async def update_user_profile(
        self,
        telegram_id: int,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
        interests: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        bio: Optional[str] = None
    ) -> Optional[User]:
        """Update user profile information"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return None
            
            # Update fields if provided
            if name is not None:
                user.name = name
            if gender is not None:
                user.gender = gender
            if age_group is not None:
                user.age_group = age_group
            if interests is not None:
                import json
                user.interests = json.dumps(interests, ensure_ascii=False) if interests else None
            if goals is not None:
                import json
                user.goals = json.dumps(goals, ensure_ascii=False) if goals else None
            if bio is not None:
                user.bio = bio
            
            # Mark as not new user after profile update
            if user.is_new_user:
                user.is_new_user = False
            
            user.last_activity = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(user)
            
            # Log profile update (temporarily disabled due to enum issue)
            # await self.log_activity(user.id, ActivityType.PROFILE_CREATED)
            
            return user
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            await self.session.rollback()
            return None
    
    async def update_last_activity(self, telegram_id: int) -> None:
        """Update user's last activity timestamp"""
        try:
            await self.session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(last_activity=datetime.utcnow())
            )
            await self.session.commit()
        except Exception as e:
            logger.error(f"Error updating last activity: {e}")
    
    async def set_user_settings(
        self,
        telegram_id: int,
        settings: Dict[str, Any]
    ) -> bool:
        """Update user settings"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            if user.settings is None:
                user.settings = {}
            
            user.settings.update(settings)
            user.last_activity = datetime.utcnow()
            
            await self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            await self.session.rollback()
            return False
    
    async def get_user_settings(self, telegram_id: int) -> Dict[str, Any]:
        """Get user settings"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if user and user.settings:
                return user.settings
            return {}
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return {}
    
    async def check_rate_limit(
        self,
        telegram_id: int,
        action: str,
        limit: int,
        window_hours: int = 24
    ) -> tuple[bool, int]:
        """Check if user has exceeded rate limit for specific action"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False, 0
            
            # VIP users have no rate limits
            if user.subscription_type == "VIP":
                return True, limit
            
            # Premium users have higher limits
            if user.subscription_type == "PREMIUM":
                limit = limit * 3
            
            # Count activities in the time window
            since = datetime.utcnow() - timedelta(hours=window_hours)
            
            result = await self.session.execute(
                select(func.count(UserActivity.id))
                .where(
                    UserActivity.user_id == user.id,
                    UserActivity.activity_type == action,
                    UserActivity.created_at >= since
                )
            )
            
            count = result.scalar() or 0
            return count < limit, limit - count
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False, 0
    
    async def log_activity(
        self,
        user_id: int,
        activity_type: ActivityType,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user activity"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                activity_name=activity_type.value,
                extra_data=details or {}
            )
            
            self.session.add(activity)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    async def get_user_stats(self, telegram_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return {}
            
            # Count various activities
            activities_result = await self.session.execute(
                select(
                    UserActivity.activity_type,
                    func.count(UserActivity.id).label('count')
                )
                .where(UserActivity.user_id == user.id)
                .group_by(UserActivity.activity_type)
            )
            
            activities = {row.activity_type: row.count for row in activities_result}
            
            # Get achievements count
            achievements_result = await self.session.execute(
                select(func.count(UserAchievement.id))
                .where(UserAchievement.user_id == user.id)
            )
            achievements_count = achievements_result.scalar() or 0
            
            return {
                'user_since': user.created_at.isoformat(),
                'last_activity': user.last_activity.isoformat() if user.last_activity else None,
                'subscription_type': user.subscription_type,
                'activities': activities,
                'achievements_count': achievements_count,
                'total_activities': sum(activities.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def delete_user(self, telegram_id: int) -> bool:
        """Delete user and all related data"""
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            # Delete user (cascade will handle related data)
            await self.session.delete(user)
            await self.session.commit()
            
            logger.info(f"User deleted: {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            await self.session.rollback()
            return False
    
    async def get_users_by_subscription(
        self,
        subscription_type: str
    ) -> List[User]:
        """Get users by subscription type"""
        try:
            result = await self.session.execute(
                select(User)
                .where(User.subscription_type == subscription_type)
                .options(selectinload(User.subscriptions))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting users by subscription: {e}")
            return []
    
    async def get_active_users(self, days: int = 7) -> List[User]:
        """Get users active in the last N days"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            result = await self.session.execute(
                select(User)
                .where(User.last_activity >= since)
                .order_by(User.last_activity.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def get_user_count_stats(self) -> Dict[str, int]:
        """Get user count statistics"""
        try:
            # Total users
            total_result = await self.session.execute(
                select(func.count(User.id))
            )
            total_users = total_result.scalar() or 0
            
            # Users by subscription type
            subscription_result = await self.session.execute(
                select(
                    User.subscription_type,
                    func.count(User.id).label('count')
                )
                .group_by(User.subscription_type)
            )
            
            by_subscription = {
                row.subscription_type: row.count 
                for row in subscription_result
            }
            
            # Active users (last 7 days)
            since = datetime.utcnow() - timedelta(days=7)
            active_result = await self.session.execute(
                select(func.count(User.id))
                .where(User.last_activity >= since)
            )
            active_users = active_result.scalar() or 0
            
            return {
                'total_users': total_users,
                'active_users_7d': active_users,
                'by_subscription': by_subscription
            }
            
        except Exception as e:
            logger.error(f"Error getting user count stats: {e}")
            return {} 