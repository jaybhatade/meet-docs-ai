"""
Property-based tests for Meet Joiner module.
Tests correctness properties using Hypothesis.
"""

import pytest
import pickle
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from hypothesis import given, strategies as st, settings
from selenium.common.exceptions import WebDriverException

from src.meet_joiner import MeetJoiner, AuthenticationError


# ============================================
# Property 1: URL validation and navigation
# Feature: meetdocs-ai-automation, Property 1: URL validation and navigation
# Validates: Requirements 1.1, 8.1
# ============================================

@given(
    st.one_of(
        # Valid Google Meet URLs
        st.builds(
            lambda code: f"https://meet.google.com/{code}",
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65), min_size=10, max_size=20)
        ),
        st.builds(
            lambda code: f"https://meet.google.co.in/{code}",
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65), min_size=10, max_size=20)
        ),
        st.builds(
            lambda code: f"http://meet.google.com/{code}",
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65), min_size=10, max_size=20)
        )
    )
)
@settings(max_examples=100, deadline=None)
def test_property_url_validation_valid_urls(meet_url):
    """
    Property 1: URL validation and navigation
    For any valid Google Meet URL format, the Meet Joiner should successfully 
    parse the URL and validate it as a proper Google Meet link.
    
    Validates: Requirements 1.1, 8.1
    """
    # Create temporary cookie file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        cookies = [{'name': 'test', 'value': 'test', 'domain': '.google.com', 'path': '/'}]
        pickle.dump(cookies, f)
        temp_cookie_path = f.name
    
    try:
        # Create MeetJoiner instance
        joiner = MeetJoiner(temp_cookie_path)
        
        # Test URL validation
        is_valid = joiner.validate_meet_url(meet_url)
        
        # Assert that valid Google Meet URLs are recognized
        assert is_valid is True, f"Valid Meet URL should be recognized: {meet_url}"
        
        # Cleanup
        joiner.close()
    finally:
        Path(temp_cookie_path).unlink(missing_ok=True)


@given(
    st.one_of(
        # Invalid URLs - wrong domain
        st.builds(
            lambda code: f"https://zoom.us/{code}",
            st.text(min_size=10, max_size=20)
        ),
        # Invalid URLs - no path
        st.just("https://meet.google.com"),
        st.just("https://meet.google.com/"),
        # Invalid URLs - wrong scheme
        st.builds(
            lambda code: f"ftp://meet.google.com/{code}",
            st.text(min_size=10, max_size=20)
        ),
        # Invalid URLs - malformed
        st.text(alphabet=st.characters(blacklist_characters='/:', min_codepoint=65), min_size=5, max_size=20)
    )
)
@settings(max_examples=100, deadline=None)
def test_property_url_validation_invalid_urls(invalid_url):
    """
    Property 1 (negative case): URL validation should reject invalid URLs
    For any invalid URL format, the Meet Joiner should reject it.
    
    Validates: Requirements 1.1, 8.1
    """
    # Create temporary cookie file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        cookies = [{'name': 'test', 'value': 'test', 'domain': '.google.com', 'path': '/'}]
        pickle.dump(cookies, f)
        temp_cookie_path = f.name
    
    try:
        # Create MeetJoiner instance
        joiner = MeetJoiner(temp_cookie_path)
        
        # Test URL validation
        is_valid = joiner.validate_meet_url(invalid_url)
        
        # Assert that invalid URLs are rejected
        assert is_valid is False, f"Invalid URL should be rejected: {invalid_url}"
        
        # Cleanup
        joiner.close()
    finally:
        Path(temp_cookie_path).unlink(missing_ok=True)


# ============================================
# Property 2: Cookie-based authentication
# Feature: meetdocs-ai-automation, Property 2: Cookie-based authentication
# Validates: Requirements 1.2
# ============================================

@given(
    st.lists(
        st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=20),
            'value': st.text(min_size=1, max_size=50),
            'domain': st.sampled_from(['.google.com', '.meet.google.com']),
            'path': st.just('/'),
            'secure': st.booleans(),
            'httpOnly': st.booleans()
        }),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
def test_property_cookie_authentication(cookies_data):
    """
    Property 2: Cookie-based authentication
    For any saved cookie file with valid authentication data, the Meet Joiner 
    should successfully load cookies without requiring credential input.
    
    Validates: Requirements 1.2
    """
    # Create temporary cookie file with generated cookies
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        pickle.dump(cookies_data, f)
        temp_cookie_path = f.name
    
    try:
        # Create MeetJoiner instance
        joiner = MeetJoiner(temp_cookie_path)
        
        # Mock the driver to avoid actual browser initialization
        mock_driver = MagicMock()
        joiner.driver = mock_driver
        
        # Test cookie loading
        result = joiner.load_cookies()
        
        # Assert cookies were loaded successfully
        assert result is True, "Cookie loading should succeed with valid cookie file"
        
        # Verify that add_cookie was called for each cookie
        assert mock_driver.add_cookie.call_count >= len(cookies_data), \
            "add_cookie should be called for each cookie in the file"
        
        # Cleanup
        joiner.close()
        
    finally:
        # Cleanup temp file
        Path(temp_cookie_path).unlink(missing_ok=True)


def test_property_cookie_authentication_missing_file():
    """
    Property 2 (error case): Cookie authentication should fail with missing file
    When cookie file doesn't exist, MeetJoiner initialization should raise FileNotFoundError.
    
    Validates: Requirements 1.2
    """
    non_existent_path = "/tmp/nonexistent_cookies_12345.pkl"
    
    # Attempt to create MeetJoiner with non-existent cookie file
    with pytest.raises(FileNotFoundError):
        MeetJoiner(non_existent_path)


# ============================================
# Property 3: AV device state before join
# Feature: meetdocs-ai-automation, Property 3: AV device state before join
# Validates: Requirements 1.3
# ============================================

@settings(max_examples=100, deadline=None)
@given(st.booleans(), st.booleans())
def test_property_av_device_state(camera_initially_on, mic_initially_on):
    """
    Property 3: AV device state before join
    For any meeting join attempt, the camera and microphone elements should be 
    in disabled state before the join button is clicked.
    
    Validates: Requirements 1.3
    """
    # Create temporary cookie file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        cookies = [{'name': 'test', 'value': 'test', 'domain': '.google.com', 'path': '/'}]
        pickle.dump(cookies, f)
        temp_cookie_path = f.name
    
    try:
        # Create MeetJoiner instance
        joiner = MeetJoiner(temp_cookie_path)
        
        # Mock the driver and WebDriverWait
        mock_driver = MagicMock()
        joiner.driver = mock_driver
        
        # Mock camera button
        mock_camera_button = MagicMock()
        camera_label = 'Turn off camera' if camera_initially_on else 'Turn on camera'
        mock_camera_button.get_attribute.return_value = camera_label
        
        # Mock microphone button
        mock_mic_button = MagicMock()
        mic_label = 'Turn off microphone' if mic_initially_on else 'Turn on microphone'
        mock_mic_button.get_attribute.return_value = mic_label
        
        # Setup mock to return buttons in sequence
        mock_driver.find_element.side_effect = [mock_camera_button, mock_mic_button]
        
        with patch('src.meet_joiner.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            
            # First call returns camera button, second returns mic button
            mock_wait_instance.until.side_effect = [mock_camera_button, mock_mic_button]
            
            # Call disable_av
            result = joiner.disable_av()
            
            # Assert that disable_av succeeded
            assert result is True, "disable_av should succeed"
            
            # If camera was initially on, verify it was clicked
            if camera_initially_on:
                mock_camera_button.click.assert_called_once()
            
            # If mic was initially on, verify it was clicked
            if mic_initially_on:
                mock_mic_button.click.assert_called_once()
            
            # Cleanup
            joiner.close()
    finally:
        Path(temp_cookie_path).unlink(missing_ok=True)


# ============================================
# Property 4: Conditional join behavior
# Feature: meetdocs-ai-automation, Property 4: Conditional join behavior
# Validates: Requirements 1.4
# ============================================

@settings(max_examples=100, deadline=None)
@given(st.booleans())
def test_property_conditional_join_behavior(is_open_meeting):
    """
    Property 4: Conditional join behavior
    For any meeting room configuration, the Meet Joiner should either click 
    "Join now" for open meetings or handle "Ask to join" for restricted meetings.
    
    Validates: Requirements 1.4
    """
    # Create temporary cookie file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        cookies = [{'name': 'test', 'value': 'test', 'domain': '.google.com', 'path': '/'}]
        pickle.dump(cookies, f)
        temp_cookie_path = f.name
    
    try:
        # Create MeetJoiner instance
        joiner = MeetJoiner(temp_cookie_path)
        
        # Mock the driver
        mock_driver = MagicMock()
        joiner.driver = mock_driver
        
        # Mock the appropriate button based on meeting type
        mock_button = MagicMock()
        
        with patch('src.meet_joiner.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            
            if is_open_meeting:
                # For open meetings, "Join now" button should be found
                mock_wait_instance.until.return_value = mock_button
                button_text = "Join now"
            else:
                # For restricted meetings, "Join now" times out, then "Ask to join" is found
                from selenium.common.exceptions import TimeoutException
                mock_wait_instance.until.side_effect = [TimeoutException(), mock_button]
                button_text = "Ask to join"
            
            # Call click_join_button
            result = joiner.click_join_button()
            
            # Assert that join button was clicked successfully
            assert result is True, f"Should successfully click '{button_text}' button"
            
            # Verify the button was clicked
            mock_button.click.assert_called_once()
            
            # Cleanup
            joiner.close()
    finally:
        Path(temp_cookie_path).unlink(missing_ok=True)
