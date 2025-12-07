"""
Meet Joiner module for MeetDocs AI automation system.
Handles automated Google Meet session joining using Selenium.
"""

import logging
import pickle
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)


class MeetJoinerError(Exception):
    """Base exception for Meet Joiner errors."""
    pass


class AuthenticationError(MeetJoinerError):
    """Raised when authentication fails."""
    pass


class JoinError(MeetJoinerError):
    """Raised when joining the meeting fails."""
    pass


class MeetJoiner:
    """Automates Google Meet session joining using Selenium."""
    
    def __init__(self, cookie_path: str):
        """
        Initialize MeetJoiner with cookie path.
        
        Args:
            cookie_path: Path to saved Google Chrome cookies file
            
        Raises:
            FileNotFoundError: If cookie file doesn't exist
        """
        self.cookie_path = Path(cookie_path)
        if not self.cookie_path.exists():
            raise FileNotFoundError(f"Cookie file not found: {cookie_path}")
        
        self.driver: Optional[webdriver.Chrome] = None
        self._in_meeting = False
        
        logger.info(f"MeetJoiner initialized with cookie path: {cookie_path}")
    
    def _init_browser(self) -> webdriver.Chrome:
        """
        Initialize Chrome browser with appropriate options.
        
        Returns:
            Configured Chrome WebDriver instance
            
        Raises:
            WebDriverException: If browser initialization fails
        """
        try:
            chrome_options = Options()
            
            # Disable notifications
            chrome_options.add_argument("--disable-notifications")
            
            # Disable GPU for stability
            chrome_options.add_argument("--disable-gpu")
            
            # Use fake UI for media devices
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            
            # Disable dev shm usage for stability in containers
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Set window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize ChromeDriver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Chrome browser initialized successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise WebDriverException(f"Browser initialization failed: {e}")
    
    def load_cookies(self) -> bool:
        """
        Load authentication cookies from file.
        
        Returns:
            True if cookies loaded successfully
            
        Raises:
            AuthenticationError: If cookie loading fails
        """
        try:
            # Navigate to Google first to set domain
            self.driver.get("https://accounts.google.com")
            time.sleep(2)
            
            # Load cookies from file
            with open(self.cookie_path, 'rb') as f:
                cookies = pickle.load(f)
            
            # Add each cookie to the browser
            for cookie in cookies:
                try:
                    # Remove expiry if present (can cause issues)
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie: {e}")
            
            logger.info("Cookies loaded successfully")
            return True
            
        except FileNotFoundError:
            logger.error(f"Cookie file not found: {self.cookie_path}")
            raise AuthenticationError(f"Cookie file not found: {self.cookie_path}")
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            raise AuthenticationError(f"Cookie loading failed: {e}")
    
    def validate_meet_url(self, meet_url: str) -> bool:
        """
        Validate Google Meet URL format.
        
        Args:
            meet_url: URL to validate
            
        Returns:
            True if URL is valid Google Meet URL
        """
        try:
            parsed = urlparse(meet_url)
            
            # Check if it's a Google Meet domain
            valid_domains = ['meet.google.com', 'meet.google.co.in']
            is_valid = (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc in valid_domains and
                len(parsed.path) > 1
            )
            
            if is_valid:
                logger.info(f"Valid Meet URL: {meet_url}")
            else:
                logger.warning(f"Invalid Meet URL: {meet_url}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def disable_av(self) -> bool:
        """
        Disable camera and microphone before joining meeting.
        
        Returns:
            True if AV devices disabled successfully
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Wait for the meeting preview page to load
            time.sleep(3)
            
            # Try to find and click camera button if it's on
            try:
                camera_button = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//button[@aria-label='Turn off camera' or contains(@aria-label, 'camera')]"
                    ))
                )
                if 'Turn off' in camera_button.get_attribute('aria-label'):
                    camera_button.click()
                    logger.info("Camera disabled")
                    time.sleep(1)
            except (TimeoutException, NoSuchElementException):
                logger.info("Camera already disabled or not found")
            
            # Try to find and click microphone button if it's on
            try:
                mic_button = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//button[@aria-label='Turn off microphone' or contains(@aria-label, 'microphone')]"
                    ))
                )
                if 'Turn off' in mic_button.get_attribute('aria-label'):
                    mic_button.click()
                    logger.info("Microphone disabled")
                    time.sleep(1)
            except (TimeoutException, NoSuchElementException):
                logger.info("Microphone already disabled or not found")
            
            logger.info("AV devices disabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable AV devices: {e}")
            return False
    
    def click_join_button(self) -> bool:
        """
        Click the appropriate join button (Join now or Ask to join).
        
        Returns:
            True if join button clicked successfully
            
        Raises:
            JoinError: If join button not found or click fails
        """
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Try to find "Join now" button first (for open meetings)
            try:
                join_button = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(., 'Join now') or contains(@aria-label, 'Join now')]"
                    ))
                )
                join_button.click()
                logger.info("Clicked 'Join now' button")
                time.sleep(2)
                return True
            except TimeoutException:
                logger.info("'Join now' button not found, trying 'Ask to join'")
            
            # Try "Ask to join" button (for restricted meetings)
            try:
                ask_button = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(., 'Ask to join') or contains(@aria-label, 'Ask to join')]"
                    ))
                )
                ask_button.click()
                logger.info("Clicked 'Ask to join' button")
                time.sleep(2)
                return True
            except TimeoutException:
                logger.error("Neither 'Join now' nor 'Ask to join' button found")
                raise JoinError("Join button not found")
            
        except Exception as e:
            logger.error(f"Failed to click join button: {e}")
            raise JoinError(f"Join button click failed: {e}")
    
    def is_in_meeting(self) -> bool:
        """
        Check if successfully joined the meeting.
        
        Returns:
            True if currently in a meeting
        """
        try:
            # Check for meeting UI elements that indicate we're in the meeting
            # Look for the leave call button or meeting controls
            try:
                self.driver.find_element(
                    By.XPATH,
                    "//button[@aria-label='Leave call' or contains(@aria-label, 'Leave')]"
                )
                self._in_meeting = True
                logger.info("Confirmed: In meeting")
                return True
            except NoSuchElementException:
                pass
            
            # Alternative: Check for meeting participant count or other indicators
            try:
                self.driver.find_element(
                    By.XPATH,
                    "//div[@data-meeting-title or contains(@class, 'meeting')]"
                )
                self._in_meeting = True
                logger.info("Confirmed: In meeting (alternative check)")
                return True
            except NoSuchElementException:
                pass
            
            self._in_meeting = False
            logger.warning("Not in meeting")
            return False
            
        except Exception as e:
            logger.error(f"Error checking meeting status: {e}")
            return False
    
    def join_meeting(self, meet_url: str) -> bool:
        """
        Join a Google Meet session.
        
        Args:
            meet_url: Google Meet URL to join
            
        Returns:
            True if successfully joined the meeting
            
        Raises:
            ValueError: If URL is invalid
            AuthenticationError: If authentication fails
            JoinError: If joining fails
        """
        try:
            # Validate URL
            if not self.validate_meet_url(meet_url):
                raise ValueError(f"Invalid Google Meet URL: {meet_url}")
            
            # Initialize browser if not already done
            if self.driver is None:
                self.driver = self._init_browser()
            
            # Load authentication cookies
            self.load_cookies()
            
            # Navigate to the meeting URL
            logger.info(f"Navigating to meeting: {meet_url}")
            self.driver.get(meet_url)
            time.sleep(3)
            
            # Disable camera and microphone
            self.disable_av()
            
            # Click join button
            self.click_join_button()
            
            # Wait a bit for the meeting to load
            time.sleep(5)
            
            # Verify we're in the meeting
            if self.is_in_meeting():
                logger.info("Successfully joined the meeting")
                return True
            else:
                logger.warning("Join attempt completed but meeting status unclear")
                return False
            
        except (ValueError, AuthenticationError, JoinError) as e:
            logger.error(f"Failed to join meeting: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during meeting join: {e}")
            raise JoinError(f"Meeting join failed: {e}")
    
    def leave_meeting(self):
        """Leave the current meeting."""
        try:
            if not self._in_meeting:
                logger.info("Not in a meeting, nothing to leave")
                return
            
            # Find and click the leave button
            leave_button = self.driver.find_element(
                By.XPATH,
                "//button[@aria-label='Leave call' or contains(@aria-label, 'Leave')]"
            )
            leave_button.click()
            logger.info("Left the meeting")
            
            self._in_meeting = False
            time.sleep(2)
            
        except NoSuchElementException:
            logger.warning("Leave button not found")
        except Exception as e:
            logger.error(f"Error leaving meeting: {e}")
    
    def close(self):
        """Close the browser and cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
                self.driver = None
                self._in_meeting = False
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
