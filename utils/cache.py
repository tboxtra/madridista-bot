"""
Caching system for API responses and computed results.
Provides in-memory caching with TTL support for performance optimization.
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from threading import Lock

class CacheEntry:
    """Represents a cache entry with metadata."""
    
    def __init__(self, data: Any, ttl: int = 3600):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Access the cache entry and update metadata."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary."""
        return {
            "data": self.data,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }

class CacheManager:
    """In-memory cache manager with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            self.stats["total_requests"] += 1
            
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self.cache[key]
                    self.stats["misses"] += 1
                    return None
                
                # Return data and update access info
                self.stats["hits"] += 1
                return entry.access()
            else:
                self.stats["misses"] += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_entries()
            
            # Store the entry
            self.cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "total_requests": 0
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = (self.stats["hits"] / max(self.stats["total_requests"], 1)) * 100
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": round(hit_rate, 2),
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "total_requests": self.stats["total_requests"]
            }
    
    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Get information about all cache entries."""
        with self.lock:
            entries = []
            for key, entry in self.cache.items():
                entries.append({
                    "key": key,
                    "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
                    "ttl": entry.ttl,
                    "access_count": entry.access_count,
                    "last_accessed": datetime.fromtimestamp(entry.last_accessed).isoformat(),
                    "is_expired": entry.is_expired()
                })
            
            return sorted(entries, key=lambda x: x["last_accessed"], reverse=True)
    
    def _evict_entries(self) -> None:
        """Evict least recently used entries."""
        if not self.cache:
            return
        
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove 10% of entries (or at least 1)
        evict_count = max(1, len(sorted_entries) // 10)
        
        for i in range(evict_count):
            key, _ = sorted_entries[i]
            del self.cache[key]
            self.stats["evictions"] += 1

class APICache:
    """Specialized cache for API responses."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def cache_api_response(self, endpoint: str, params: Dict[str, Any], 
                          response: Any, ttl: int = 3600) -> None:
        """Cache API response."""
        key = self._generate_api_key(endpoint, params)
        self.cache.set(key, response, ttl)
    
    def get_cached_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached API response."""
        key = self._generate_api_key(endpoint, params)
        return self.cache.get(key)
    
    def _generate_api_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for API request."""
        # Sort params for consistent key generation
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        
        # Create hash of endpoint + params
        key_string = f"{endpoint}:{param_string}"
        return hashlib.md5(key_string.encode()).hexdigest()

class ToolCache:
    """Specialized cache for tool results."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def cache_tool_result(self, tool_name: str, args: Dict[str, Any], 
                         result: Any, ttl: int = 1800) -> None:
        """Cache tool result."""
        key = self._generate_tool_key(tool_name, args)
        self.cache.set(key, result, ttl)
    
    def get_cached_result(self, tool_name: str, args: Dict[str, Any]) -> Optional[Any]:
        """Get cached tool result."""
        key = self._generate_tool_key(tool_name, args)
        return self.cache.get(key)
    
    def _generate_tool_key(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Generate cache key for tool call."""
        # Sort args for consistent key generation
        sorted_args = sorted(args.items())
        args_string = json.dumps(sorted_args, sort_keys=True)
        
        # Create hash of tool name + args
        key_string = f"tool:{tool_name}:{args_string}"
        return hashlib.md5(key_string.encode()).hexdigest()

class UserCache:
    """Specialized cache for user-specific data."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def cache_user_data(self, user_id: str, data_type: str, data: Any, ttl: int = 7200) -> None:
        """Cache user-specific data."""
        key = f"user:{user_id}:{data_type}"
        self.cache.set(key, data, ttl)
    
    def get_cached_user_data(self, user_id: str, data_type: str) -> Optional[Any]:
        """Get cached user data."""
        key = f"user:{user_id}:{data_type}"
        return self.cache.get(key)
    
    def clear_user_cache(self, user_id: str) -> None:
        """Clear all cached data for a user."""
        with self.cache.lock:
            keys_to_remove = [
                key for key in self.cache.cache.keys()
                if key.startswith(f"user:{user_id}:")
            ]
            
            for key in keys_to_remove:
                del self.cache.cache[key]

# Global cache instances
cache_manager = CacheManager(max_size=1000, default_ttl=3600)
api_cache = APICache(cache_manager)
tool_cache = ToolCache(cache_manager)
user_cache = UserCache(cache_manager)

# Cache decorator for functions
def cached(ttl: int = 3600, key_func: Optional[callable] = None):
    """Decorator to cache function results."""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_string = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_string.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Utility functions
def cleanup_cache() -> int:
    """Clean up expired cache entries."""
    return cache_manager.cleanup_expired()

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache_manager.get_stats()

def clear_all_cache() -> None:
    """Clear all cache entries."""
    cache_manager.clear()
