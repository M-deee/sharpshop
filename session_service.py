"""Redis-based session management for conversation state."""
import json
import logging
from typing import Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing conversation sessions in Redis."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.ttl = 3600  # 1 hour
    
    async def _get_client(self):
        """Lazy initialization of Redis client."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client
    
    def _get_key(self, phone_number: str) -> str:
        """Generate Redis key for a phone number."""
        return f"session:{phone_number}"
    
    async def get_state(self, phone_number: str) -> Optional[dict]:
        """Retrieve conversation state from Redis."""
        try:
            client = await self._get_client()
            key = self._get_key(phone_number)
            data = await client.get(key)
            
            if data:
                state = json.loads(data)
                logger.info(f"Loaded state for {phone_number}")
                return state
            
            logger.info(f"No existing state for {phone_number}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to get state from Redis: {e}")
            raise
    
    async def save_state(self, phone_number: str, state: dict) -> bool:
        """Save conversation state to Redis with TTL."""
        try:
            client = await self._get_client()
            key = self._get_key(phone_number)
            data = json.dumps(state)
            
            await client.setex(key, self.ttl, data)
            logger.info(f"Saved state for {phone_number} with {self.ttl}s TTL")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save state to Redis: {e}")
            raise
    
    async def delete_state(self, phone_number: str) -> bool:
        """Delete conversation state from Redis."""
        try:
            client = await self._get_client()
            key = self._get_key(phone_number)
            result = await client.delete(key)
            logger.info(f"Deleted state for {phone_number}")
            return result > 0
        
        except Exception as e:
            logger.error(f"Failed to delete state from Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()