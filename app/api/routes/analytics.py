"""Analytics endpoints for bot statistics"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.user import User
from app.models.analytics import UserActivity
from app.models.analysis import TextAnalysis
from app.models.profile import PartnerProfile
from app.models.subscription import Subscription
from app.utils.enums import ActivityType, SubscriptionType
from app.core.logging import logger

router = APIRouter()


@router.get("/analytics/overview")
async def get_analytics_overview(session: AsyncSession = Depends(get_db)):
    """Get general analytics overview"""
    
    try:
        # Total users
        total_users_result = await session.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar() or 0
        
        # Active users (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users_result = await session.execute(
            select(func.count(User.id.distinct()))
            .select_from(UserActivity)
            .join(User)
            .where(UserActivity.created_at >= week_ago)
        )
        active_users = active_users_result.scalar() or 0
        
        # Total analyses
        total_analyses_result = await session.execute(
            select(func.count(TextAnalysis.id))
        )
        total_analyses = total_analyses_result.scalar() or 0
        
        # Total profiles
        total_profiles_result = await session.execute(
            select(func.count(PartnerProfile.id))
        )
        total_profiles = total_profiles_result.scalar() or 0
        
        # Subscription distribution
        subscription_stats = await session.execute(
            select(
                User.subscription_type,
                func.count(User.id).label('count')
            )
            .group_by(User.subscription_type)
        )
        
        subscription_distribution = {
            row.subscription_type.value: row.count 
            for row in subscription_stats
        }
        
        return {
            "overview": {
                "total_users": total_users,
                "active_users_7d": active_users,
                "total_analyses": total_analyses,
                "total_profiles": total_profiles
            },
            "subscription_distribution": subscription_distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/users")
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get user analytics for specified period"""
    
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        # New users by day
        new_users_result = await session.execute(
            select(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            )
            .where(User.created_at >= since)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        
        new_users_by_day = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in new_users_result
        ]
        
        # Active users by day
        active_users_result = await session.execute(
            select(
                func.date(UserActivity.created_at).label('date'),
                func.count(func.distinct(UserActivity.user_id)).label('count')
            )
            .where(UserActivity.created_at >= since)
            .group_by(func.date(UserActivity.created_at))
            .order_by(func.date(UserActivity.created_at))
        )
        
        active_users_by_day = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in active_users_result
        ]
        
        # Activity types distribution
        activity_result = await session.execute(
            select(
                UserActivity.activity_type,
                func.count(UserActivity.id).label('count')
            )
            .where(UserActivity.created_at >= since)
            .group_by(UserActivity.activity_type)
        )
        
        activity_distribution = {
            row.activity_type.value: row.count
            for row in activity_result
        }
        
        return {
            "period_days": days,
            "new_users_by_day": new_users_by_day,
            "active_users_by_day": active_users_by_day,
            "activity_distribution": activity_distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/usage")
async def get_usage_analytics(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get feature usage analytics"""
    
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        # Text analyses by day
        analyses_result = await session.execute(
            select(
                func.date(TextAnalysis.created_at).label('date'),
                func.count(TextAnalysis.id).label('count')
            )
            .where(TextAnalysis.created_at >= since)
            .group_by(func.date(TextAnalysis.created_at))
            .order_by(func.date(TextAnalysis.created_at))
        )
        
        analyses_by_day = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in analyses_result
        ]
        
        # Profiles created by day
        profiles_result = await session.execute(
            select(
                func.date(PartnerProfile.created_at).label('date'),
                func.count(PartnerProfile.id).label('count')
            )
            .where(PartnerProfile.created_at >= since)
            .group_by(func.date(PartnerProfile.created_at))
            .order_by(func.date(PartnerProfile.created_at))
        )
        
        profiles_by_day = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in profiles_result
        ]
        
        # Risk level distribution in analyses
        risk_result = await session.execute(
            select(
                TextAnalysis.risk_assessment,
                func.count(TextAnalysis.id).label('count')
            )
            .where(TextAnalysis.created_at >= since)
            .group_by(TextAnalysis.risk_assessment)
        )
        
        risk_distribution = {
            row.risk_assessment.value: row.count
            for row in risk_result
        }
        
        # Average manipulation scores
        manipulation_result = await session.execute(
            select(func.avg(TextAnalysis.manipulation_score))
            .where(
                and_(
                    TextAnalysis.created_at >= since,
                    TextAnalysis.manipulation_score.isnot(None)
                )
            )
        )
        
        avg_manipulation_score = manipulation_result.scalar() or 0.0
        
        return {
            "period_days": days,
            "analyses_by_day": analyses_by_day,
            "profiles_by_day": profiles_by_day,
            "risk_distribution": risk_distribution,
            "avg_manipulation_score": round(float(avg_manipulation_score), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/revenue")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get revenue and subscription analytics"""
    
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        # Revenue by day
        revenue_result = await session.execute(
            select(
                func.date(Subscription.created_at).label('date'),
                func.sum(Subscription.price).label('revenue'),
                func.count(Subscription.id).label('subscriptions')
            )
            .where(
                and_(
                    Subscription.created_at >= since,
                    Subscription.payment_status == 'completed'
                )
            )
            .group_by(func.date(Subscription.created_at))
            .order_by(func.date(Subscription.created_at))
        )
        
        revenue_by_day = [
            {
                "date": row.date.isoformat(),
                "revenue": float(row.revenue or 0),
                "subscriptions": row.subscriptions
            }
            for row in revenue_result
        ]
        
        # Subscription type breakdown
        subscription_breakdown_result = await session.execute(
            select(
                Subscription.subscription_type,
                func.count(Subscription.id).label('count'),
                func.sum(Subscription.price).label('revenue')
            )
            .where(
                and_(
                    Subscription.created_at >= since,
                    Subscription.payment_status == 'completed'
                )
            )
            .group_by(Subscription.subscription_type)
        )
        
        subscription_breakdown = {
            row.subscription_type.value: {
                "count": row.count,
                "revenue": float(row.revenue or 0)
            }
            for row in subscription_breakdown_result
        }
        
        # Total metrics
        total_revenue = sum(item["revenue"] for item in revenue_by_day)
        total_subscriptions = sum(item["subscriptions"] for item in revenue_by_day)
        
        # Conversion rate (subscriptions / active users)
        active_users_result = await session.execute(
            select(func.count(func.distinct(UserActivity.user_id)))
            .where(UserActivity.created_at >= since)
        )
        active_users = active_users_result.scalar() or 1
        
        conversion_rate = (total_subscriptions / active_users) * 100 if active_users > 0 else 0
        
        return {
            "period_days": days,
            "total_revenue": total_revenue,
            "total_subscriptions": total_subscriptions,
            "conversion_rate": round(conversion_rate, 2),
            "revenue_by_day": revenue_by_day,
            "subscription_breakdown": subscription_breakdown,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/retention")
async def get_retention_analytics(session: AsyncSession = Depends(get_db)):
    """Get user retention analytics"""
    
    try:
        # 7-day retention
        week_ago = datetime.utcnow() - timedelta(days=7)
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        
        # Users who joined 7-14 days ago
        cohort_users_result = await session.execute(
            select(func.count(User.id))
            .where(
                and_(
                    User.created_at >= two_weeks_ago,
                    User.created_at < week_ago
                )
            )
        )
        cohort_users = cohort_users_result.scalar() or 0
        
        # How many of those were active in the last 7 days
        retained_users_result = await session.execute(
            select(func.count(func.distinct(UserActivity.user_id)))
            .join(User)
            .where(
                and_(
                    User.created_at >= two_weeks_ago,
                    User.created_at < week_ago,
                    UserActivity.created_at >= week_ago
                )
            )
        )
        retained_users = retained_users_result.scalar() or 0
        
        retention_rate_7d = (retained_users / cohort_users * 100) if cohort_users > 0 else 0
        
        # 30-day retention
        month_ago = datetime.utcnow() - timedelta(days=30)
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        
        cohort_users_30_result = await session.execute(
            select(func.count(User.id))
            .where(
                and_(
                    User.created_at >= two_months_ago,
                    User.created_at < month_ago
                )
            )
        )
        cohort_users_30 = cohort_users_30_result.scalar() or 0
        
        retained_users_30_result = await session.execute(
            select(func.count(func.distinct(UserActivity.user_id)))
            .join(User)
            .where(
                and_(
                    User.created_at >= two_months_ago,
                    User.created_at < month_ago,
                    UserActivity.created_at >= month_ago
                )
            )
        )
        retained_users_30 = retained_users_30_result.scalar() or 0
        
        retention_rate_30d = (retained_users_30 / cohort_users_30 * 100) if cohort_users_30 > 0 else 0
        
        return {
            "retention_7d": {
                "cohort_size": cohort_users,
                "retained_users": retained_users,
                "retention_rate": round(retention_rate_7d, 2)
            },
            "retention_30d": {
                "cohort_size": cohort_users_30,
                "retained_users": retained_users_30,
                "retention_rate": round(retention_rate_30d, 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting retention analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 