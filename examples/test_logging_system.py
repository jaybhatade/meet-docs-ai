"""
Example script demonstrating the logging system.
Shows how logging works across different modules and log levels.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, setup_logging
import logging


def demonstrate_logging():
    """Demonstrate the logging system with various log levels."""
    
    # Create configuration
    config = Config.from_env()
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Setup logging
    setup_logging(config)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("MeetDocs AI - Logging System Demonstration")
    print("="*60)
    print(f"\nLog files will be created in: {config.log_dir}")
    print(f"  - Main log: {config.log_dir}/meetdocs.log")
    print(f"  - Error log: {config.log_dir}/meetdocs_errors.log")
    print(f"\nLog level: {config.log_level}")
    print("\n" + "="*60)
    
    # Demonstrate different log levels
    logger.debug("This is a DEBUG message - detailed information for diagnosing problems")
    logger.info("This is an INFO message - general informational messages")
    logger.warning("This is a WARNING message - something unexpected happened")
    logger.error("This is an ERROR message - a serious problem occurred")
    logger.critical("This is a CRITICAL message - a very serious error")
    
    print("\n" + "="*60)
    print("Logging demonstration complete!")
    print("="*60)
    print("\nCheck the log files to see the output:")
    print(f"  - Console: Shows INFO and above")
    print(f"  - {config.log_dir}/meetdocs.log: Shows all levels (DEBUG and above)")
    print(f"  - {config.log_dir}/meetdocs_errors.log: Shows only ERROR and CRITICAL")
    print("\n")


def demonstrate_module_logging():
    """Demonstrate logging from different modules."""
    
    print("\n" + "="*60)
    print("Demonstrating logging from different modules")
    print("="*60 + "\n")
    
    # Simulate logging from different modules
    modules = [
        'meet_joiner',
        'audio_capture',
        'transcriber',
        'translator',
        'summarizer',
        'exporter'
    ]
    
    for module_name in modules:
        module_logger = logging.getLogger(f'src.{module_name}')
        module_logger.info(f"{module_name} module initialized successfully")
        module_logger.debug(f"{module_name} module debug information")
    
    print("\nModule logging demonstration complete!")
    print("Check the log files to see module names in the format:")
    print("  [timestamp] [level] [module] [function] - message\n")


def demonstrate_error_logging():
    """Demonstrate error logging with exception information."""
    
    print("\n" + "="*60)
    print("Demonstrating error logging with exceptions")
    print("="*60 + "\n")
    
    logger = logging.getLogger(__name__)
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Mathematical error occurred: {e}", exc_info=True)
    
    try:
        # Simulate another error
        with open('nonexistent_file.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError as e:
        logger.error(f"File operation failed: {e}")
    
    print("\nError logging demonstration complete!")
    print("Check meetdocs_errors.log to see only error messages\n")


if __name__ == '__main__':
    # Run demonstrations
    demonstrate_logging()
    demonstrate_module_logging()
    demonstrate_error_logging()
    
    print("="*60)
    print("All demonstrations complete!")
    print("="*60)
