#!/usr/bin/env python3
"""
Discord Account Generator Pro - Main Entry Point

LEGAL DISCLAIMER:
This software is provided for EDUCATIONAL AND RESEARCH PURPOSES ONLY.
Users are solely responsible for compliance with Discord's Terms of Service
and all applicable laws. The developers disclaim all liability for misuse.

Copyright © 2024 Security Tools Pro. All rights reserved.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.application import DiscordGeneratorApp
from src.core.config_manager import ConfigManager
from src.core.license_manager import LicenseManager
from src.core.logger import setup_logging
from src.gui.main_window import MainWindow
from src.utils.system_check import SystemChecker
from src.utils.legal_disclaimer import show_legal_disclaimer

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Discord Account Generator Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Launch GUI
  python main.py --cli              # Command line interface
  python main.py --batch 10         # Generate 10 accounts
  python main.py --config custom.yaml  # Use custom config
  python main.py --validate-license    # Validate license key
        """
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Run in command line interface mode'
    )
    
    parser.add_argument(
        '--gui', 
        action='store_true',
        help='Run in graphical user interface mode (default)'
    )
    
    parser.add_argument(
        '--config', 
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--batch', 
        type=int,
        help='Number of accounts to generate in batch mode'
    )
    
    parser.add_argument(
        '--threads', 
        type=int,
        help='Number of threads to use for generation'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file for generated accounts'
    )
    
    parser.add_argument(
        '--proxy-file', 
        type=str,
        help='Path to proxy list file'
    )
    
    parser.add_argument(
        '--validate-license', 
        action='store_true',
        help='Validate license key and exit'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information and exit'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--no-disclaimer', 
        action='store_true',
        help='Skip legal disclaimer (for automated usage)'
    )
    
    return parser.parse_args()

def show_version():
    """Display version information."""
    print("Discord Account Generator Pro")
    print("Version: 1.0.0")
    print("Copyright © 2024 Security Tools Pro")
    print("License: Commercial")
    print()
    print("Support:")
    print("  Telegram: @danirueaq")
    print("  Channel: t.me/Sectools1")

def validate_environment():
    """Validate the runtime environment."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required")
            return False
            
        # Check required directories
        required_dirs = ['src', 'config', 'logs', 'data']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                
        return True
        
    except Exception as e:
        print(f"Environment validation failed: {e}")
        return False

def main():
    """Main application entry point."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Show version and exit if requested
        if args.version:
            show_version()
            return 0
            
        # Validate environment
        if not validate_environment():
            return 1
            
        # Setup logging
        log_level = logging.DEBUG if args.debug else logging.INFO
        setup_logging(level=log_level)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Discord Account Generator Pro")
        
        # Show legal disclaimer
        if not args.no_disclaimer:
            if not show_legal_disclaimer():
                logger.info("User declined legal disclaimer")
                return 0
                
        # Load configuration
        config_manager = ConfigManager(args.config)
        if not config_manager.load_config():
            logger.error("Failed to load configuration")
            return 1
            
        # Validate license
        license_manager = LicenseManager(config_manager)
        if args.validate_license:
            if license_manager.validate_license():
                print("License is valid")
                return 0
            else:
                print("License is invalid")
                return 1
                
        if not license_manager.validate_license():
            logger.error("Invalid or expired license")
            print("Please contact support for a valid license key")
            print("Telegram: @danirueaq")
            return 1
            
        # System compatibility check
        system_checker = SystemChecker()
        if not system_checker.check_compatibility():
            logger.error("System compatibility check failed")
            return 1
            
        # Initialize application
        app = DiscordGeneratorApp(config_manager, license_manager)
        
        # Determine run mode
        if args.cli or args.batch:
            # Command line interface mode
            logger.info("Running in CLI mode")
            
            # Override config with command line arguments
            if args.batch:
                config_manager.set('generation.batch_size', args.batch)
            if args.threads:
                config_manager.set('generation.max_threads', args.threads)
            if args.output:
                config_manager.set('export.output_file', args.output)
            if args.proxy_file:
                config_manager.set('proxy.sources[0].path', args.proxy_file)
                
            # Run batch generation
            result = app.run_batch_generation()
            return 0 if result else 1
            
        else:
            # GUI mode (default)
            logger.info("Running in GUI mode")
            
            # Check GUI dependencies
            try:
                import tkinter
                import customtkinter
            except ImportError as e:
                logger.error(f"GUI dependencies not available: {e}")
                print("GUI mode requires tkinter and customtkinter")
                print("Install with: pip install customtkinter")
                return 1
                
            # Launch GUI
            gui = MainWindow(app)
            gui.run()
            return 0
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        print("Please check the logs for more details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
