import os

# Required environment variables
REQUIRED = ["TELEGRAM_BOT_TOKEN", "FOOTBALL_DATA_API_KEY", "TZ"]

def validate_env():
    """Validate required environment variables on startup"""
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")
    
    # Optional but recommended
    optional = ["OPENAI_API_KEY", "RAPIDAPI_KEY", "SOFA_USER_AGENT", "SOFA_TEAM_ID"]
    missing_optional = [k for k in optional if not os.getenv(k)]
    if missing_optional:
        print(f"Warning: Optional env vars missing: {', '.join(missing_optional)}")
    
    print("Environment validation passed")
