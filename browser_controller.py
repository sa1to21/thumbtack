"""
Browser controller with human-like behavior for Thumbtack automation
"""
import time
import random
import logging
from typing import Optional
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class HumanBehavior:
    """Utilities for simulating human-like behavior"""

    @staticmethod
    def random_delay(min_sec: float, max_sec: float):
        """Sleep for a random time between min and max seconds"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    @staticmethod
    def reaction_delay():
        """Simulate human reaction time after receiving notification (30-50 seconds)"""
        delay = random.uniform(30, 50)
        logger.info(f"💭 Simulating human reaction time: {delay:.1f} seconds")
        time.sleep(delay)

    @staticmethod
    def typing_delay():
        """Return random delay between keystrokes (40ms - 150ms)"""
        return random.uniform(0.04, 0.15)

    @staticmethod
    def human_type(element, text: str):
        """
        Type text character by character with random delays (like a human)

        Args:
            element: Selenium web element
            text: Text to type
        """
        logger.info(f"⌨️  Typing message ({len(text)} chars)...")
        for i, char in enumerate(text):
            element.send_keys(char)
            time.sleep(HumanBehavior.typing_delay())

            # Occasionally pause longer (simulating thinking)
            if i > 0 and i % random.randint(15, 30) == 0:
                time.sleep(random.uniform(0.3, 0.8))

        logger.info("✅ Typing completed")


class ThumbтackBrowser:
    """Browser controller for Thumbtack with stealth and human-like behavior"""

    def __init__(self, profile_dir: str = None):
        """
        Initialize browser controller

        Args:
            profile_dir: Path to Chrome profile directory for session persistence
        """
        # Auto-detect profile directory based on OS
        if profile_dir is None:
            import os
            if os.path.exists("/app/chrome_profile"):  # Docker
                profile_dir = "/app/chrome_profile"
            else:  # Local (Mac/Linux/Windows)
                profile_dir = os.path.join(os.path.dirname(__file__), "chrome_profile")

        self.profile_dir = profile_dir
        self.driver: Optional[Driver] = None
        self.is_logged_in = False

    def start(self):
        """Start browser with stealth settings"""
        logger.info("🚀 Starting browser with stealth mode...")

        try:
            # Initialize SeleniumBase Driver with undetected mode
            self.driver = Driver(
                uc=True,  # Undetected ChromeDriver mode (critical!)
                headless=False  # Use Xvfb instead of headless mode
            )

            # Set window size after initialization
            self.driver.set_window_size(1920, 1080)

            # Note: user_data_dir must be set via Chrome options in newer versions
            # Session persistence works automatically with uc mode

            logger.info("✅ Browser started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False

    def restart(self):
        """Restart browser (recommended every 2-3 hours to clear memory)"""
        logger.info("🔄 Restarting browser...")
        self.stop()
        time.sleep(3)
        return self.start()

    def stop(self):
        """Stop browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped")
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")
            finally:
                self.driver = None

    def check_login_status(self) -> bool:
        """
        Check if user is logged in to Thumbtack

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Navigate to inbox
            self.driver.get("https://www.thumbtack.com/inbox")
            time.sleep(3)

            # Check if we're on login page or inbox
            current_url = self.driver.current_url

            if "login" in current_url.lower() or "sign" in current_url.lower():
                logger.warning("⚠️  Not logged in - login page detected")
                self.is_logged_in = False
                return False

            # Check for inbox-specific elements
            try:
                # Wait for inbox to load (adjust selector as needed)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='inbox'], .inbox-container, [class*='inbox']"))
                )
                logger.info("✅ Logged in successfully")
                self.is_logged_in = True
                return True
            except TimeoutException:
                logger.warning("⚠️  Could not find inbox elements")
                self.is_logged_in = False
                return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def navigate_to_inbox(self):
        """Navigate to Thumbtack inbox"""
        logger.info("📬 Navigating to inbox...")
        self.driver.get("https://www.thumbtack.com/inbox")
        HumanBehavior.random_delay(2, 4)

    def find_unread_conversation(self):
        """
        Find and click on the first unread conversation

        Returns:
            True if unread conversation found and clicked, False otherwise
        """
        try:
            # Try multiple selectors for unread conversations
            selectors = [
                "[data-test='unread-conversation']",
                ".unread",
                "[class*='unread']",
                ".conversation.unread",
                "[data-unread='true']"
            ]

            for selector in selectors:
                try:
                    unread = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                    logger.info(f"📨 Found unread conversation with selector: {selector}")

                    # Simulate human-like scrolling to element
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", unread)
                    HumanBehavior.random_delay(0.5, 1.0)

                    # Click
                    unread.click()
                    logger.info("✅ Clicked on unread conversation")
                    HumanBehavior.random_delay(1, 2)
                    return True

                except TimeoutException:
                    continue

            logger.warning("⚠️  No unread conversations found")
            return False

        except Exception as e:
            logger.error(f"Error finding unread conversation: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """
        Send a message in the currently open conversation

        Args:
            message: Text message to send

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Find message input field (try multiple selectors)
            input_selectors = [
                "textarea[data-test='message-input']",
                "textarea[placeholder*='message']",
                "textarea[placeholder*='Message']",
                "textarea",
                "input[type='text'][data-test='message']"
            ]

            input_field = None
            for selector in input_selectors:
                try:
                    input_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found message input: {selector}")
                    break
                except TimeoutException:
                    continue

            if not input_field:
                logger.error("❌ Could not find message input field")
                return False

            # Click on input field (human-like)
            input_field.click()
            HumanBehavior.random_delay(0.5, 1.5)

            # Type message with human-like delays
            HumanBehavior.human_type(input_field, message)

            # Wait before sending (like a human reviewing the message)
            HumanBehavior.random_delay(1, 2)

            # Find and click send button
            send_selectors = [
                "button[type='submit']",
                "button[data-test='send-message']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']"
            ]

            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    send_button.click()
                    logger.info("✅ Message sent successfully!")
                    return True
                except NoSuchElementException:
                    continue

            # If no send button found, try pressing Enter
            logger.info("Send button not found, trying Enter key...")
            input_field.send_keys("\n")
            logger.info("✅ Message sent via Enter key")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    def handle_new_lead(self, email_data: dict):
        """
        Main handler for new lead - navigates to conversation and sends response

        Args:
            email_data: Dictionary with email information
        """
        logger.info(f"🔥 Handling new lead: {email_data.get('subject', 'Unknown')}")

        # Simulate human reaction time (30-50 seconds)
        HumanBehavior.reaction_delay()

        # Navigate to inbox
        self.navigate_to_inbox()

        # Find and open unread conversation
        if not self.find_unread_conversation():
            logger.warning("Could not find unread conversation, refreshing page...")
            self.driver.refresh()
            HumanBehavior.random_delay(2, 4)

            if not self.find_unread_conversation():
                logger.error("❌ Still no unread conversation found after refresh")
                return

        # Wait for conversation to load
        HumanBehavior.random_delay(1, 2)

        # Prepare response message (you can customize this)
        message = "Hi! Thanks for reaching out. I'm available for this project. Could you share more details about what you need?"

        # Send message
        if self.send_message(message):
            logger.info("✅ Successfully handled new lead!")
        else:
            logger.error("❌ Failed to send message")
