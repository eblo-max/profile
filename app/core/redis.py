"""Redis client configuration and utilities"""

import json
from typing import Any, Optional, Union
from redis.asyncio import Redis, ConnectionPool
from loguru import logger

from app.core.config import settings


class RedisClient:
    """Redis client wrapper with utilities"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.is_available = False
    
    async def init(self) -> None:
        """Initialize Redis connection"""
        try:
            pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                decode_responses=True,
            )
            self.redis = Redis(connection_pool=pool)
            
            # Test connection
            await self.redis.ping()
            self.is_available = True
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed (fallback to memory): {e}")
            self.is_available = False
            # In development, we can continue without Redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with JSON deserialization"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis with JSON serialization"""
        if not self.redis:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis.set(key, serialized_value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in Redis"""
        if not self.redis:
            return None
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error for key {key}: {e}")
            return None
    
    async def set_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, int]:
        """
        Check and set rate limit
        Returns (allowed, remaining_requests)
        """
        if not self.redis:
            return True, limit
        
        try:
            current = await self.redis.get(key)
            if current is None:
                await self.redis.setex(key, window, 1)
                return True, limit - 1
            
            current_count = int(current)
            if current_count >= limit:
                return False, 0
            
            await self.redis.incr(key)
            return True, limit - current_count - 1
            
        except Exception as e:
            logger.error(f"Rate limit error for key {key}: {e}")
            return True, limit
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Redis connection closed")


# Global Redis client instance
redis_client = RedisClient()


async def init_redis() -> None:
    """Initialize Redis client"""
    try:
        await redis_client.init()
    except Exception as e:
        logger.warning(f"⚠️ Redis initialization failed, continuing without cache: {e}")


async def get_redis() -> RedisClient:
    """Dependency to get Redis client"""
    return redis_client 


async def close_redis() -> None:
    """Close Redis connection"""
    try:
        await redis_client.close()
    except Exception as e:
        logger.warning(f"⚠️ Redis close failed: {e}") 