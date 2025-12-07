"""
Pytest configuration and shared fixtures for MeetDocs AI tests.
"""

import pytest
import pickle
import tempfile
from pathlib import Path


@pytest.fixture
def temp_cookie_file():
    """Create a temporary cookie file for testing."""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        # Create a minimal valid cookie structure
        cookies = [
            {
                'name': 'test_cookie',
                'value': 'test_value',
                'domain': '.google.com',
                'path': '/',
                'secure': True,
                'httpOnly': False
            }
        ]
        pickle.dump(cookies, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def invalid_cookie_file():
    """Create a temporary invalid cookie file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("invalid cookie data")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
