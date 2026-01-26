"""
IMAP IDLE email monitor for instant notifications from Gmail
"""
import time
import logging
from typing import Callable, Optional
from imap_tools import MailBox, AND
from email.header import decode_header

logger = logging.getLogger(__name__)


class EmailMonitor:
    """Monitors Gmail inbox for new Thumbtack lead notifications using IMAP IDLE"""

    def __init__(self, email: str, password: str, callback: Callable):
        """
        Initialize email monitor

        Args:
            email: Gmail address
            password: Gmail app password (not regular password!)
            callback: Function to call when new lead email arrives
        """
        self.email = email
        self.password = password
        self.callback = callback
        self.mailbox: Optional[MailBox] = None

    def connect(self):
        """Establish connection to Gmail IMAP server"""
        try:
            self.mailbox = MailBox('imap.gmail.com')
            self.mailbox.login(self.email, self.password)
            logger.info(f"✅ Connected to Gmail: {self.email}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Gmail: {e}")
            return False

    def disconnect(self):
        """Close connection to Gmail"""
        if self.mailbox:
            try:
                self.mailbox.logout()
                logger.info("Disconnected from Gmail")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    def is_thumbtack_lead(self, msg) -> bool:
        """
        Check if email is a new lead notification from Thumbtack

        Args:
            msg: Email message object

        Returns:
            True if this is a Thumbtack lead notification
        """
        # Check sender
        sender = msg.from_.lower() if hasattr(msg, 'from_') else ''
        if 'thumbtack.com' not in sender:
            return False

        # Check subject for lead keywords
        subject = msg.subject.lower() if msg.subject else ''
        lead_keywords = ['new lead', 'new customer', 'new request', 'sent you a message']

        return any(keyword in subject for keyword in lead_keywords)

    def start_monitoring(self):
        """
        Start IMAP IDLE monitoring
        This method blocks and runs indefinitely, calling the callback when new emails arrive
        """
        if not self.mailbox:
            if not self.connect():
                raise ConnectionError("Could not connect to Gmail")

        logger.info("👀 Starting email monitoring (IMAP IDLE mode)...")
        logger.info("Waiting for new Thumbtack lead notifications...")

        # Select inbox folder
        self.mailbox.folder.set('INBOX')

        # IMAP IDLE loop - this keeps connection open and receives instant push notifications
        while True:
            try:
                # Start IDLE mode - this blocks until new email arrives or timeout (29 min)
                responses = self.mailbox.idle.wait(timeout=1740)  # 29 minutes (IMAP standard)

                if responses:
                    logger.info(f"📧 New email detected, checking...")

                    # Fetch recent unread messages
                    for msg in self.mailbox.fetch(AND(seen=False), mark_seen=False, limit=5, reverse=True):
                        if self.is_thumbtack_lead(msg):
                            logger.info(f"🔥 NEW THUMBTACK LEAD: {msg.subject}")

                            # Extract email data
                            email_data = {
                                'subject': msg.subject,
                                'from': msg.from_,
                                'date': msg.date,
                                'text': msg.text or '',
                                'html': msg.html or ''
                            }

                            # Call the callback with email data
                            try:
                                self.callback(email_data)
                            except Exception as e:
                                logger.error(f"❌ Error in callback: {e}")

                            # Mark as read so we don't process it again
                            self.mailbox.flag([msg.uid], ['\\Seen'], True)
                        else:
                            logger.debug(f"Skipping non-lead email: {msg.subject}")

                # If IDLE timed out (29 min), reconnect to keep connection alive
                else:
                    logger.debug("IDLE timeout, reconnecting...")

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                logger.info("Reconnecting in 30 seconds...")
                time.sleep(30)

                # Try to reconnect
                self.disconnect()
                if not self.connect():
                    logger.error("Could not reconnect, waiting 60 seconds...")
                    time.sleep(60)

        self.disconnect()
