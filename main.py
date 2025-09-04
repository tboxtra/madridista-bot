import os, random, sys
from dotenv import load_dotenv

from prompts.fan_prompts import PROMPTS
from ai_engine.gpt_engine import generate_short_post
from utils.validators import clamp_tweet

def main():
    load_dotenv(override=False)

    # 1) Generate post text
    prompt = random.choice(PROMPTS)
    text = generate_short_post(prompt, max_chars=240)
    text = clamp_tweet(text, max_chars=280)
    print("Draft:", text)

    # DRY RUN?
    if os.getenv("DRY_RUN", "false").lower() == "true":
        print("DRY_RUN=true → not posting.")
        return

    # TOTP secret is now in environment, no argument needed
    print("🔐 Using TOTP secret from environment")

    # Only import TwitterAPI.io functions when actually posting
    from platforms.twitterapi_client import (
        login_step1_get_login_data,
        login_step2_get_session,
        create_tweet
    )

    # 2) Login → session
    print("Logging in via TwitterAPI.io…")
    session = login_step1_get_login_data()
    print("Got session:", session[:12] + "…")

    # 3) Post
    print("Posting tweet…")
    res = create_tweet(session, text)
    print("✅ Posted:", res)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", e)
