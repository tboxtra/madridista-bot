import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import pytz

# Default timezone - can be overridden by environment variable
DEFAULT_TIMEZONE = os.getenv("BOT_TIMEZONE", "UTC")
DEFAULT_LOCALE = os.getenv("BOT_LOCALE", "en_US")

def get_current_time(timezone_name: Optional[str] = None) -> datetime:
    """
    Get current time in specified timezone or default timezone.
    Falls back to UTC if timezone is invalid.
    """
    try:
        tz = pytz.timezone(timezone_name or DEFAULT_TIMEZONE)
        return datetime.now(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        # Fallback to UTC if timezone is invalid
        return datetime.now(timezone.utc)

def get_utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)

def format_time_until(target_time: Union[datetime, str], source_time: Optional[datetime] = None) -> str:
    """
    Format time difference in a human-readable way.
    
    Args:
        target_time: Target datetime or ISO string
        source_time: Source datetime (defaults to current time)
    
    Returns:
        Formatted string like "5m", "2h 30m", "3d", etc.
    """
    if isinstance(target_time, str):
        try:
            # Handle different ISO formats properly
            if target_time.endswith('Z'):
                target_time = target_time[:-1] + '+00:00'
            elif '+' not in target_time and 'T' in target_time:
                target_time = target_time + '+00:00'
            target_time = datetime.fromisoformat(target_time)
        except ValueError:
            return "Unknown time"
    
    if source_time is None:
        source_time = get_utc_now()
    
    # Ensure both times are timezone-aware
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    if source_time.tzinfo is None:
        source_time = source_time.replace(tzinfo=timezone.utc)
    
    # Convert both to UTC for accurate comparison
    target_utc = target_time.astimezone(timezone.utc)
    source_utc = source_time.astimezone(timezone.utc)
    
    diff = target_utc - source_utc
    total_seconds = diff.total_seconds()
    
    if total_seconds <= 0:
        return "Now"
    
    # Convert to minutes
    total_minutes = int(total_seconds // 60)
    
    if total_minutes < 1:
        return "Less than 1m"
    elif total_minutes < 60:
        return f"{total_minutes}m"
    elif total_minutes < 1440:  # 24 hours
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {minutes}m"
    else:
        days = total_minutes // 1440
        remaining_hours = (total_minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days}d"
        else:
            return f"{days}d {remaining_hours}h"

def format_match_time(match_time: Union[datetime, str], timezone_name: Optional[str] = None) -> str:
    """
    Format match time in a user-friendly way with timezone awareness.
    
    Args:
        match_time: Match datetime or ISO string
        timezone_name: Target timezone for display
    
    Returns:
        Formatted string like "Today 20:00", "Tomorrow 15:30", "Dec 15 20:00"
    """
    if isinstance(match_time, str):
        try:
            # Handle different ISO formats properly
            if match_time.endswith('Z'):
                match_time = match_time[:-1] + '+00:00'
            elif '+' not in match_time and 'T' in match_time:
                match_time = match_time + '+00:00'
            match_time = datetime.fromisoformat(match_time)
        except ValueError:
            return "Unknown time"
    
    current_time = get_utc_now()  # Always use UTC for comparison
    
    # Ensure match time is timezone-aware
    if match_time.tzinfo is None:
        match_time = match_time.replace(tzinfo=timezone.utc)
    
    # Convert both to UTC for accurate comparison
    match_utc = match_time.astimezone(timezone.utc)
    current_utc = current_time.astimezone(timezone.utc)
    
    # Calculate time difference
    diff = match_utc - current_utc
    total_seconds = diff.total_seconds()
    
    # Format based on how far in the future
    if total_seconds <= 0:
        return "Live now"
    elif total_seconds <= 3600:  # 1 hour
        minutes = int(total_seconds // 60)
        return f"Starting in {minutes}m"
    elif total_seconds <= 86400:  # 24 hours
        if match_utc.date() == current_utc.date():
            return f"Today at {match_utc.strftime('%H:%M')}"
        else:
            return f"Tomorrow at {match_utc.strftime('%H:%M')}"
    elif total_seconds <= 604800:  # 7 days
        return match_utc.strftime("%a at %H:%M")
    else:
        return match_utc.strftime("%b %d at %H:%M")

def get_time_status(match_time: Union[datetime, str]) -> str:
    """
    Get match status based on time (Live, Starting soon, Upcoming, etc.)
    
    Args:
        match_time: Match datetime or ISO string
    
    Returns:
        Status string with appropriate emoji
    """
    if isinstance(match_time, str):
        try:
            # Handle different ISO formats properly
            if match_time.endswith('Z'):
                match_time = match_time[:-1] + '+00:00'
            elif '+' not in match_time and 'T' in match_time:
                match_time = match_time + '+00:00'
            match_time = datetime.fromisoformat(match_time)
        except ValueError:
            return "📅 Unknown"
    
    current_time = get_utc_now()
    
    # Ensure match time is timezone-aware
    if match_time.tzinfo is None:
        match_time = match_time.replace(tzinfo=timezone.utc)
    
    # Convert both to UTC for accurate comparison
    match_utc = match_time.astimezone(timezone.utc)
    current_utc = current_time.astimezone(timezone.utc)
    
    diff = match_utc - current_utc
    total_seconds = diff.total_seconds()
    
    if total_seconds <= -7200:  # 2 hours ago
        return "🏁 Finished"
    elif total_seconds <= 0:
        return "⚡ Live"
    elif total_seconds <= 900:  # 15 minutes
        return "🚨 Starting soon"
    elif total_seconds <= 3600:  # 1 hour
        return "⏰ Starting soon"
    elif total_seconds <= 86400:  # 24 hours
        return "📅 Today/Tomorrow"
    else:
        return "📅 Upcoming"

def format_last_updated() -> str:
    """Format current time as 'last updated' timestamp."""
    current_time = get_current_time()
    return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

def get_timezone_info() -> str:
    """Get current timezone information."""
    try:
        current_time = get_current_time()
        return f"Current time: {current_time.strftime('%H:%M:%S %Z')} ({current_time.tzinfo})"
    except Exception:
        return "Current time: UTC"

def is_match_live(match_time: Union[datetime, str], duration_minutes: int = 120) -> bool:
    """
    Check if a match is currently live.
    
    Args:
        match_time: Match start time
        duration_minutes: Expected match duration in minutes
    
    Returns:
        True if match is live, False otherwise
    """
    if isinstance(match_time, str):
        try:
            # Handle different ISO formats properly
            if match_time.endswith('Z'):
                match_time = match_time[:-1] + '+00:00'
            elif '+' not in match_time and 'T' in match_time:
                match_time = match_time + '+00:00'
            match_time = datetime.fromisoformat(match_time)
        except ValueError:
            return False
    
    current_time = get_utc_now()
    
    # Ensure match time is timezone-aware
    if match_time.tzinfo is None:
        match_time = match_time.replace(tzinfo=timezone.utc)
    
    # Convert both to UTC for accurate comparison
    match_utc = match_time.astimezone(timezone.utc)
    current_utc = current_time.astimezone(timezone.utc)
    
    match_end = match_utc + timedelta(minutes=duration_minutes)
    
    return match_utc <= current_utc <= match_end

def get_next_match_time(matches: list) -> Optional[datetime]:
    """
    Get the next upcoming match time from a list of matches.
    
    Args:
        matches: List of match dictionaries with 'date' or 'utcDate' keys
    
    Returns:
        Next match datetime or None if no upcoming matches
    """
    current_time = get_utc_now()
    next_match = None
    min_diff = float('inf')
    
    for match in matches:
        match_time_str = match.get('date') or match.get('utcDate')
        if not match_time_str:
            continue
            
        try:
            # Handle different ISO formats properly
            if match_time_str.endswith('Z'):
                match_time_str = match_time_str[:-1] + '+00:00'
            elif '+' not in match_time_str and 'T' in match_time_str:
                match_time_str = match_time_str + '+00:00'
            
            match_time = datetime.fromisoformat(match_time_str)
            if match_time.tzinfo is None:
                match_time = match_time.replace(tzinfo=timezone.utc)
            
            # Convert to UTC for accurate comparison
            match_utc = match_time.astimezone(timezone.utc)
            current_utc = current_time.astimezone(timezone.utc)
            
            diff = (match_utc - current_utc).total_seconds()
            if 0 < diff < min_diff:
                min_diff = diff
                next_match = match_time
        except ValueError:
            continue
    
    return next_match
