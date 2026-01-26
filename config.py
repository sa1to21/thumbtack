"""
Configuration settings for Thumbtack auto-responder
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings loaded from environment variables"""

    # Gmail settings (IMAP)
    GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # NOT your regular Gmail password!

    # Chrome profile directory (for session persistence)
    # Auto-detect based on environment
    _default_profile = "/app/chrome_profile" if os.path.exists("/app") else os.path.join(os.path.dirname(__file__), "chrome_profile")
    CHROME_PROFILE_DIR = os.getenv("CHROME_PROFILE_DIR", _default_profile)

    # Browser restart interval (in seconds, default 2 hours)
    BROWSER_RESTART_INTERVAL = int(os.getenv("BROWSER_RESTART_INTERVAL", "7200"))

    # Thumbtack settings
    THUMBTACK_INBOX_URL = "https://www.thumbtack.com/inbox"

    # Response template (can be customized)
    DEFAULT_MESSAGE = os.getenv(
        "DEFAULT_MESSAGE",
        "Hi! Thanks for reaching out. I'm available for this project. Could you share more details about what you need?"
    )

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    _default_log = "/app/logs/bot.log" if os.path.exists("/app") else os.path.join(os.path.dirname(__file__), "logs", "bot.log")
    LOG_FILE = os.getenv("LOG_FILE", _default_log)

    # Human behavior settings
    # Reaction time after receiving email (seconds)
    REACTION_TIME_MIN = float(os.getenv("REACTION_TIME_MIN", "30"))
    REACTION_TIME_MAX = float(os.getenv("REACTION_TIME_MAX", "50"))

    # Typing speed (seconds between characters)
    TYPING_SPEED_MIN = float(os.getenv("TYPING_SPEED_MIN", "0.04"))
    TYPING_SPEED_MAX = float(os.getenv("TYPING_SPEED_MAX", "0.15"))

    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        errors = []

        if not cls.GMAIL_EMAIL:
            errors.append("GMAIL_EMAIL is not set")

        if not cls.GMAIL_APP_PASSWORD:
            errors.append("GMAIL_APP_PASSWORD is not set")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def print_config(cls):
        """Print current configuration (hiding sensitive data)"""
        print("=== Configuration ===")
        print(f"Gmail: {cls.GMAIL_EMAIL}")
        print(f"Gmail password: {'*' * len(cls.GMAIL_APP_PASSWORD) if cls.GMAIL_APP_PASSWORD else 'NOT SET'}")
        print(f"Chrome profile: {cls.CHROME_PROFILE_DIR}")
        print(f"Browser restart: {cls.BROWSER_RESTART_INTERVAL}s ({cls.BROWSER_RESTART_INTERVAL/3600:.1f}h)")
        print(f"Log level: {cls.LOG_LEVEL}")
        print(f"Log file: {cls.LOG_FILE}")
        print(f"Reaction time: {cls.REACTION_TIME_MIN}-{cls.REACTION_TIME_MAX}s")
        print("===================")
