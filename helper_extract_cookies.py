#!/usr/bin/env python3
"""
Cookie Extraction Helper for MeetDocs AI

This script helps you extract Google authentication cookies from your Chrome browser
for use with the MeetDocs AI automation system.

IMPORTANT: You must be logged into Google in Chrome before running this script.

Usage:
    python helper_extract_cookies.py [--output cookies.pkl]

The script will:
1. Launch Chrome browser
2. Navigate to Google accounts page
3. Wait for you to log in (if not already logged in)
4. Extract and save authentication cookies
5. Save cookies to the specified file (default: cookies.pkl)

Security Note:
- The cookie file contains sensitive authentication data
- Never commit cookies.pkl to version control
- Keep the file secure and private
- Cookies may expire and need to be refreshed periodically
"""

import argparse
import pickle
import sys
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("ERROR: Required packages not installed.", file=sys.stderr)
    print("Please install: pip install selenium webdriver-manager", file=sys.stderr)
    sys.exit(1)


def extract_cookies(output_path: str = "cookies.pkl") -> bool:
    """
    Extract Google authentication cookies from Chrome.
    
    Args:
        output_path: Path where cookies will be saved
        
    Returns:
        True if cookies extracted successfully
    """
    driver = None
    
    try:
        print("=" * 80)
        print("MeetDocs AI - Cookie Extraction Helper")
        print("=" * 80)
        print()
        
        # Initialize Chrome browser
        print("Initializing Chrome browser...")
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--window-size=1200,800")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Browser launched successfully")
        print()
        
        # Navigate to Google accounts
        print("Navigating to Google accounts page...")
        driver.get("https://accounts.google.com")
        time.sleep(2)
        
        print("✓ Loaded Google accounts page")
        print()
        
        # Instructions for user
        print("=" * 80)
        print("INSTRUCTIONS:")
        print("=" * 80)
        print()
        print("1. If you're not logged in, please log in to your Google account now")
        print("2. Make sure you're logged into the account you want to use for Meet")
        print("3. Once logged in, return to this terminal")
        print("4. Press ENTER when you're ready to extract cookies...")
        print()
        
        input("Press ENTER to continue...")
        
        # Give a moment for any redirects to complete
        time.sleep(2)
        
        # Extract cookies
        print()
        print("Extracting cookies...")
        cookies = driver.get_cookies()
        
        if not cookies:
            print("⚠ WARNING: No cookies found. Make sure you're logged in.", file=sys.stderr)
            return False
        
        print(f"✓ Found {len(cookies)} cookie(s)")
        
        # Save cookies to file
        output_file = Path(output_path)
        with open(output_file, 'wb') as f:
            pickle.dump(cookies, f)
        
        print(f"✓ Cookies saved to: {output_file.absolute()}")
        print()
        
        # Verify the saved file
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✓ Cookie file created successfully ({file_size} bytes)")
        
        print()
        print("=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print()
        print("Next steps:")
        print(f"1. Update your .env file with: COOKIE_PATH={output_path}")
        print("2. Keep this file secure and private")
        print("3. Add cookies.pkl to your .gitignore file")
        print("4. You can now run MeetDocs AI with these cookies")
        print()
        print("Note: Cookies may expire after some time. If authentication fails,")
        print("      run this script again to refresh your cookies.")
        print()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to extract cookies: {e}", file=sys.stderr)
        print()
        print("Troubleshooting:")
        print("  1. Ensure Chrome is installed on your system")
        print("  2. Check your internet connection")
        print("  3. Try closing other Chrome instances")
        print("  4. Make sure you have the latest Chrome version")
        return False
        
    finally:
        # Close browser
        if driver:
            print("Closing browser...")
            driver.quit()
            print("✓ Browser closed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract Google authentication cookies for MeetDocs AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python helper_extract_cookies.py
  python helper_extract_cookies.py --output my_cookies.pkl

Security Warning:
  The cookie file contains sensitive authentication data.
  Keep it secure and never commit it to version control.
        """
    )
    
    parser.add_argument(
        '--output',
        '-o',
        default='cookies.pkl',
        help='Output path for cookie file (default: cookies.pkl)'
    )
    
    args = parser.parse_args()
    
    # Check if output file already exists
    if Path(args.output).exists():
        print(f"WARNING: File '{args.output}' already exists.")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)
        print()
    
    success = extract_cookies(args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
