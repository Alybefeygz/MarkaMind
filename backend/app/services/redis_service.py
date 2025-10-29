# -*- coding: utf-8 -*-
"""
Redis Service
Handles Redis connections and token blacklisting
"""

import redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching and token blacklisting"""

    def __init__(self):
        """Initialize Redis connection"""
        self._client = None
        self._connect()

    def _connect(self):
        """Establish Redis connection"""
        try:
            if settings.redis_url:
                # Use Redis URL if provided
                self._client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={}
                )
            else:
                # Use individual Redis configuration
                self._client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={}
                )

            # Test connection
            self._client.ping()
            logger.info("Redis connection established successfully")

        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            self._client = None

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except:
            return False

    def reconnect(self):
        """Reconnect to Redis"""
        self._connect()

    def blacklist_token(self, jti: str, expires_in: int) -> bool:
        """
        Add token JTI to blacklist

        Args:
            jti: Token JTI (unique identifier)
            expires_in: Seconds until token expires

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, attempting reconnect")
            self.reconnect()
            if not self.is_connected():
                logger.error("Cannot blacklist token - Redis unavailable")
                return False

        try:
            key = f"blacklist:token:{jti}"
            result = self._client.setex(key, expires_in, "blacklisted")

            if result:
                logger.debug(f"Token {jti} blacklisted for {expires_in} seconds")
                return True
            else:
                logger.error(f"Failed to blacklist token {jti}")
                return False

        except Exception as e:
            logger.error(f"Error blacklisting token {jti}: {e}")
            return False

    def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if token JTI is blacklisted

        Args:
            jti: Token JTI to check

        Returns:
            True if blacklisted, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, assuming token not blacklisted")
            return False

        try:
            key = f"blacklist:token:{jti}"
            exists = self._client.exists(key)

            if exists:
                logger.debug(f"Token {jti} is blacklisted")
                return True
            else:
                logger.debug(f"Token {jti} is not blacklisted")
                return False

        except Exception as e:
            logger.error(f"Error checking token blacklist {jti}: {e}")
            return False

    def remove_from_blacklist(self, jti: str) -> bool:
        """
        Remove token JTI from blacklist

        Args:
            jti: Token JTI to remove

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot remove from blacklist")
            return False

        try:
            key = f"blacklist:token:{jti}"
            result = self._client.delete(key)

            if result:
                logger.debug(f"Token {jti} removed from blacklist")
                return True
            else:
                logger.debug(f"Token {jti} was not in blacklist")
                return True  # Not being in blacklist is OK

        except Exception as e:
            logger.error(f"Error removing token from blacklist {jti}: {e}")
            return False

    def set_cache(self, key: str, value: Any, expires_in: Optional[int] = None) -> bool:
        """
        Set cache value

        Args:
            key: Cache key
            value: Value to cache
            expires_in: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot set cache")
            return False

        try:
            # Serialize value to JSON
            serialized_value = json.dumps(value) if not isinstance(value, str) else value

            if expires_in:
                result = self._client.setex(key, expires_in, serialized_value)
            else:
                result = self._client.set(key, serialized_value)

            if result:
                logger.debug(f"Cache set for key: {key}")
                return True
            else:
                logger.error(f"Failed to set cache for key: {key}")
                return False

        except Exception as e:
            logger.error(f"Error setting cache {key}: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """
        Get cache value

        Args:
            key: Cache key

        Returns:
            Cached value if exists, None otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot get cache")
            return None

        try:
            value = self._client.get(key)

            if value is None:
                logger.debug(f"Cache miss for key: {key}")
                return None

            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"Error getting cache {key}: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        """
        Delete cache value

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot delete cache")
            return False

        try:
            result = self._client.delete(key)

            if result:
                logger.debug(f"Cache deleted for key: {key}")
                return True
            else:
                logger.debug(f"Cache key not found: {key}")
                return True  # Key not existing is OK

        except Exception as e:
            logger.error(f"Error deleting cache {key}: {e}")
            return False

    def set_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Set rate limit for identifier

        Args:
            identifier: Rate limit identifier (e.g., IP, user ID)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        if not self.is_connected():
            logger.warning("Redis not connected, allowing request")
            return True, limit - 1, window_seconds

        try:
            key = f"rate_limit:{identifier}"

            # Use sliding window log approach
            current_time = int(self._client.time()[0])
            pipeline = self._client.pipeline()

            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, current_time - window_seconds)

            # Count current entries
            pipeline.zcard(key)

            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})

            # Set expiration
            pipeline.expire(key, window_seconds)

            results = pipeline.execute()
            current_count = results[1] + 1  # +1 for the request we just added

            if current_count <= limit:
                remaining = limit - current_count
                reset_time = window_seconds
                logger.debug(f"Rate limit OK for {identifier}: {current_count}/{limit}")
                return True, remaining, reset_time
            else:
                # Remove the request we just added since it exceeds limit
                self._client.zrem(key, str(current_time))
                remaining = 0
                reset_time = window_seconds
                logger.debug(f"Rate limit exceeded for {identifier}: {current_count}/{limit}")
                return False, remaining, reset_time

        except Exception as e:
            logger.error(f"Error setting rate limit for {identifier}: {e}")
            # In case of error, allow the request
            return True, limit - 1, window_seconds

    def clear_rate_limit(self, identifier: str) -> bool:
        """
        Clear rate limit for identifier

        Args:
            identifier: Rate limit identifier to clear

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot clear rate limit")
            return False

        try:
            key = f"rate_limit:{identifier}"
            result = self._client.delete(key)

            logger.debug(f"Rate limit cleared for {identifier}")
            return True

        except Exception as e:
            logger.error(f"Error clearing rate limit for {identifier}: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Perform Redis health check

        Returns:
            Health status dictionary
        """
        try:
            if not self._client:
                return {
                    "status": "unhealthy",
                    "connected": False,
                    "error": "Redis client not initialized"
                }

            # Ping Redis
            ping_result = self._client.ping()

            # Get Redis info
            info = self._client.info()

            return {
                "status": "healthy",
                "connected": True,
                "ping": ping_result,
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }


# Global instance
redis_service = RedisService()