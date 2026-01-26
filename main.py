#!/usr/bin/env python3
"""
Thumbtack Auto-Responder Bot

Main entry point that coordinates email monitoring and browser automation
to automatically respond to new Thumbtack leads with human-like behavior.
"""
import logging
import sys
import time
import threading
from datetime import datetime, timedelta

from config import Config
from email_monitor import EmailMonitor
from browser_controller import ThumbтackBrowser


# Setup logging
def setup_logging():
    """Configure logging to both file and console"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logs directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

    # File handler (UTF-8 for emoji support)
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler (UTF-8 for emoji support on Windows)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    console_handler.setFormatter(logging.Formatter(log_format))

    # Fix Windows console encoding for emoji
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)


class ThumbtackBot:
    """Main bot orchestrator"""

    def __init__(self):
        self.browser: ThumbтackBrowser = None
        self.email_monitor: EmailMonitor = None
        self.last_browser_restart = datetime.now()
        self.is_running = False

    def initialize(self):
        """Initialize browser and check login status"""
        logger.info("=" * 60)
        logger.info("🚀 Thumbtack Auto-Responder Bot Starting...")
        logger.info("=" * 60)

        # Validate configuration
        try:
            Config.validate()
            Config.print_config()
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            logger.error("Please create a .env file based on .env.example")
            sys.exit(1)

        # Initialize browser
        logger.info("Initializing browser...")
        self.browser = ThumbтackBrowser(profile_dir=Config.CHROME_PROFILE_DIR)

        if not self.browser.start():
            logger.error("❌ Failed to start browser")
            sys.exit(1)

        # Check if logged in
        logger.info("Checking Thumbtack login status...")
        if not self.browser.check_login_status():
            logger.error("❌ Not logged in to Thumbtack!")
            logger.error("Please login manually:")
            logger.error("1. The browser window should be open (check Xvfb or VNC)")
            logger.error("2. Navigate to https://www.thumbtack.com/login")
            logger.error("3. Login with your credentials")
            logger.error("4. The session will be saved for future use")
            logger.error("\nFor Docker: You may need to use VNC or run this locally first to establish session")

            # Keep browser open for manual login
            logger.info("Keeping browser open for 5 minutes for manual login...")
            time.sleep(300)

            # Check again
            if not self.browser.check_login_status():
                logger.error("Still not logged in. Exiting...")
                sys.exit(1)

        logger.info("✅ Browser initialized and logged in")

    def handle_new_lead(self, email_data: dict):
        """
        Callback function called by email monitor when new lead arrives

        Args:
            email_data: Dictionary containing email information
        """
        logger.info("=" * 60)
        logger.info(f"🔔 NEW LEAD NOTIFICATION")
        logger.info(f"From: {email_data.get('from', 'Unknown')}")
        logger.info(f"Subject: {email_data.get('subject', 'Unknown')}")
        logger.info(f"Date: {email_data.get('date', 'Unknown')}")
        logger.info("=" * 60)

        try:
            # Check if browser needs restart (every N hours)
            if datetime.now() - self.last_browser_restart > timedelta(seconds=Config.BROWSER_RESTART_INTERVAL):
                logger.info("⏰ Time for scheduled browser restart...")
                self.browser.restart()
                self.last_browser_restart = datetime.now()

                # Re-check login after restart
                if not self.browser.check_login_status():
                    logger.error("❌ Lost login session after restart!")
                    return

            # Handle the lead
            self.browser.handle_new_lead(email_data)

        except Exception as e:
            logger.error(f"❌ Error handling lead: {e}", exc_info=True)

    def start_monitoring(self):
        """Start email monitoring (blocking call)"""
        logger.info("Initializing email monitor...")

        self.email_monitor = EmailMonitor(
            email=Config.GMAIL_EMAIL,
            password=Config.GMAIL_APP_PASSWORD,
            callback=self.handle_new_lead
        )

        if not self.email_monitor.connect():
            logger.error("❌ Failed to connect to Gmail")
            sys.exit(1)

        logger.info("✅ Email monitor connected")
        logger.info("=" * 60)
        logger.info("🟢 BOT IS NOW RUNNING")
        logger.info("Waiting for new Thumbtack leads...")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        self.is_running = True

        try:
            # This blocks indefinitely, waiting for emails
            self.email_monitor.start_monitoring()
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping bot...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
            self.shutdown()
            sys.exit(1)

    def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down...")
        self.is_running = False

        if self.email_monitor:
            self.email_monitor.disconnect()

        if self.browser:
            self.browser.stop()

        logger.info("✅ Shutdown complete")


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Create and initialize bot
    bot = ThumbtackBot()
    bot.initialize()

    # Start monitoring (this blocks)
    bot.start_monitoring()


if __name__ == "__main__":
    main()
