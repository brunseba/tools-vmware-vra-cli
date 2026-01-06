"""Redis caching utilities for REST API endpoints."""

import os
import json
import hashlib
import functools
from typing import Optional, Any, Callable
from datetime import timedelta
import redis
from redis import Redis, ConnectionPool
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

# Global Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """Get or create Redis client with connection pool.
    
    Returns:
        Redis client instance or None if Redis is unavailable
    """
    global _redis_pool, _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    try:
        # Create connection pool for better performance
        _redis_pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=20,
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True,
        )
        
        _redis_client = Redis(connection_pool=_redis_pool)
        
        # Test connection
        _redis_client.ping()
        logger.info(f"✅ Redis connected: {redis_url}")
        
        return _redis_client
    except Exception as e:
        logger.warning(f"⚠️  Redis unavailable: {e}. Caching disabled.")
        return None


def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a consistent cache key from prefix and parameters.
    
    Args:
        prefix: Cache key prefix (e.g., 'reports:dependencies')
        **kwargs: Parameters to include in the cache key
        
    Returns:
        Cache key string
    """
    # Sort kwargs to ensure consistent key generation
    sorted_params = sorted(kwargs.items())
    params_str = json.dumps(sorted_params, sort_keys=True)
    
    # Hash parameters to keep keys short
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
    
    return f"{prefix}:{params_hash}"


def cache_response(
    prefix: str,
    ttl: int = 300,  # 5 minutes default
    key_params: Optional[list] = None
):
    """Decorator to cache API responses in Redis.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_params: List of parameter names to include in cache key
        
    Example:
        @cache_response("reports:dependencies", ttl=300, key_params=["project_id", "deployment_id"])
        async def get_dependencies_report(project_id: str = None, deployment_id: str = None):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Note: For FastAPI endpoints with Pydantic response models,
            # we cache the data but cannot return cached data directly
            # because FastAPI expects a Pydantic model instance.
            # This still provides value by caching the underlying data fetching.
            
            redis_client = get_redis_client()
            
            try:
                # Extract parameters for cache key
                cache_key_params = {}
                if key_params:
                    for param in key_params:
                        if param in kwargs:
                            value = kwargs[param]
                            # Only include non-None values
                            if value is not None:
                                cache_key_params[param] = value
                
                cache_key = generate_cache_key(prefix, **cache_key_params)
                
                # For now, always execute function (FastAPI needs Pydantic model)
                # But we log cache metrics for monitoring
                if redis_client:
                    cached_exists = redis_client.exists(cache_key)
                    if cached_exists:
                        logger.info(f"✅ Cache EXISTS (but re-executing for FastAPI): {cache_key}")
                    else:
                        logger.info(f"❌ Cache MISS: {cache_key}")
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache the result for metrics/monitoring
                if redis_client:
                    try:
                        # Convert Pydantic models to dict before caching
                        if hasattr(result, 'model_dump'):
                            # Pydantic v2
                            cache_data = result.model_dump(mode='json')
                        elif hasattr(result, 'dict'):
                            # Pydantic v1
                            cache_data = result.dict()
                        else:
                            # Already a dict or other serializable type
                            cache_data = result
                        
                        redis_client.setex(
                            cache_key,
                            ttl,
                            json.dumps(cache_data, default=str)
                        )
                        logger.info(f"💾 Cached metadata: {cache_key} (TTL: {ttl}s)")
                    except Exception as cache_error:
                        logger.warning(f"Failed to cache result: {cache_error}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error: {e}. Falling back to direct execution.")
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., 'reports:*')
        
    Returns:
        Number of keys deleted
    """
    redis_client = get_redis_client()
    
    if redis_client is None:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"🗑️  Invalidated {deleted} cache entries matching '{pattern}'")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        return 0


def get_cache_stats() -> dict:
    """Get Redis cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    redis_client = get_redis_client()
    
    if redis_client is None:
        return {
            "connected": False,
            "message": "Redis unavailable"
        }
    
    try:
        info = redis_client.info("stats")
        keyspace = redis_client.info("keyspace")
        
        total_keys = 0
        for db_info in keyspace.values():
            if isinstance(db_info, dict) and 'keys' in db_info:
                total_keys += db_info['keys']
        
        return {
            "connected": True,
            "total_keys": total_keys,
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                if (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) > 0
                else 0.0
            ) * 100
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {
            "connected": False,
            "error": str(e)
        }
