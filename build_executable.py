#!/usr/bin/env python3
"""Build script for creating standalone executables with PyInstaller."""

import argparse
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build standalone executable for Backlog Backup tool"
    )
    parser.add_argument(
        "--one-file", action="store_true", 
        help="Create a single executable file instead of a directory"
    )
    parser.add_argument(
        "--no-console", action="store_true", 
        help="Hide the console window (Windows only)"
    )
    parser.add_argument(
        "--output-dir", default="./dist",
        help="Output directory for the built executable (default: ./dist)"
    )
    parser.add_argument(
        "--name", default=None,
        help="Name of the output file (defaults to 'backlog-backup' with platform-specific suffix)"
    )
    return parser.parse_args()

def get_platform_name():
    """Get platform name for executable suffix."""
    system = platform.system().lower()
    if system == "windows":
        return "win"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system

def build_executable(args):
    """Build the executable using PyInstaller."""
    try:
        # Ensure PyInstaller is installed
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller>=5.8.0"],
            check=True
        )
        
        # Generate executable name with platform suffix if not specified
        executable_name = args.name if args.name else f"backlog-backup-{get_platform_name()}"
        
        # Build PyInstaller command
        cmd = [
            "pyinstaller",
            "-n", executable_name,
            "--clean",
        ]
        
        if args.one_file:
            cmd.append("--onefile")
            # For one-file executables, add -y to force overwrite
            cmd.append("-y")
        else:
            cmd.append("--onedir")
            # For one-directory executables, add -y to force overwrite
            cmd.append("-y")
            
        if args.no_console and platform.system().lower() == "windows":
            cmd.append("--noconsole")
            
        # Add output directory
        output_dir = Path(args.output_dir).absolute()
        cmd.extend(["--distpath", str(output_dir)])
        
        # Main script to package
        cmd.append("backlog_backup/cli.py")
        
        logger.info(f"Building executable with command: {' '.join(cmd)}")
        logger.info(f"This may take a few minutes...")
        
        # Run PyInstaller
        subprocess.run(cmd, check=True)
        
        # Output location for user
        if args.one_file:
            if platform.system().lower() == "windows":
                final_path = output_dir / f"{executable_name}.exe"
            else:
                final_path = output_dir / executable_name
        else:
            final_path = output_dir / executable_name
            
        logger.info(f"Build completed successfully!")
        logger.info(f"Executable available at: {final_path}")
        return 0

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during build process: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

def main():
    """Main entry point for the build script."""
    args = parse_args()
    return build_executable(args)

if __name__ == "__main__":
    sys.exit(main())