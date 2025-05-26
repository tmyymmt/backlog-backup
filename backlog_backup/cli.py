"""Command-line interface for Backlog Backup tool."""

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .backup.issues import backup_issues
from .backup.wiki import backup_wiki
from .backup.files import backup_files
from .backup.git import backup_git
from .backup.svn import backup_svn


def setup_logging(verbose: bool = False) -> None:
    """Configure logging settings.

    Args:
        verbose: If True, sets logging level to DEBUG, otherwise INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Backlog Backup - Tool for backing up Backlog project data"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Authentication and Backlog domain settings
    parser.add_argument(
        "--domain", required=True, help="Backlog domain (e.g., 'example.backlog.com')"
    )
    parser.add_argument(
        "--api-key", required=True, help="Backlog API key"
    )
    
    # Project settings
    parser.add_argument(
        "--project", required=True, help="Backlog project key to backup"
    )
    
    # Output directory
    parser.add_argument(
        "--output", "-o", default="./backup", 
        help="Output directory for backup (default: './backup')"
    )
    
    # What to backup
    parser.add_argument(
        "--issues", action="store_true", help="Backup project issues"
    )
    parser.add_argument(
        "--wiki", action="store_true", help="Backup project wiki"
    )
    parser.add_argument(
        "--files", action="store_true", help="Backup project files"
    )
    parser.add_argument(
        "--git", action="store_true", help="Backup Git repositories"
    )
    parser.add_argument(
        "--svn", action="store_true", help="Backup Subversion repositories"
    )
    parser.add_argument(
        "--all", action="store_true", help="Backup everything"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    args = parse_args()
    setup_logging(args.verbose)
    
    logging.info(f"Starting Backlog backup for project: {args.project}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output) / args.project
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine what to backup
    backup_all = args.all
    
    try:
        if backup_all or args.issues:
            backup_issues(args.domain, args.api_key, args.project, output_dir)
            
        if backup_all or args.wiki:
            backup_wiki(args.domain, args.api_key, args.project, output_dir)
            
        if backup_all or args.files:
            backup_files(args.domain, args.api_key, args.project, output_dir)
            
        if backup_all or args.git:
            backup_git(args.domain, args.api_key, args.project, output_dir)
            
        if backup_all or args.svn:
            backup_svn(args.domain, args.api_key, args.project, output_dir)
            
        logging.info(f"Backup completed successfully. Files saved to {output_dir}")
        return 0
        
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        if args.verbose:
            logging.exception("Detailed error information:")
        return 1


if __name__ == "__main__":
    sys.exit(main())