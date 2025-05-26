"""Command-line interface for Backlog Backup tool."""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Modified imports for PyInstaller compatibility
try:
    from backlog_backup import __version__
    from backlog_backup.api.client import BacklogAPIClient
    from backlog_backup.backup.issues import backup_issues
    from backlog_backup.backup.wiki import backup_wiki
    from backlog_backup.backup.files import backup_files
    from backlog_backup.backup.git import backup_git
    from backlog_backup.backup.svn import backup_svn
except ImportError:
    # Fallback to relative imports for normal package usage
    from . import __version__
    from .api.client import BacklogAPIClient
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
        "--api-key", required=False, help="Backlog API key (can also be set via BACKLOG_API_KEY environment variable)"
    )
    
    # Project settings
    project_group = parser.add_mutually_exclusive_group()
    project_group.add_argument(
        "--project", help="Backlog project key to backup"
    )
    project_group.add_argument(
        "--all-projects", action="store_true", help="Backup all accessible projects"
    )
    project_group.add_argument(
        "--list-projects", action="store_true", help="List all accessible projects"
    )
    
    # Project filter settings
    parser.add_argument(
        "--include-all-space-projects", action="store_true", 
        help="Include all projects in the space, not just those the user has access to (requires admin privileges)"
    )
    parser.add_argument(
        "--archived-projects", choices=["all", "archived-only", "non-archived-only"], default="all",
        help="Filter projects by archive status (default: 'all')"
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


def list_projects(
    client: BacklogAPIClient,
    all_projects: bool = False,
    archived_filter: str = "all"
) -> None:
    """List all accessible projects.
    
    Args:
        client: Backlog API client
        all_projects: If True, includes all projects in the space (requires admin privileges)
        archived_filter: Filter projects by archive status ("all", "archived-only", or "non-archived-only")
    """
    try:
        # Convert filter choice to API parameter
        archived = None
        if archived_filter == "archived-only":
            archived = True
        elif archived_filter == "non-archived-only":
            archived = False
            
        projects = client.get_projects(all_projects=all_projects, archived=archived)
        print("\nAccessible Backlog Projects:")
        print("-" * 95)
        print(f"{'Project Key':<15} {'Project Name':<50} {'Project ID':<10} {'Archived':<10}")
        print("-" * 95)
        for project in projects:
            archived_status = "Yes" if project.get("archived", False) else "No"
            print(f"{project['projectKey']:<15} {project['name']:<50} {project['id']:<10} {archived_status:<10}")
        print()
    except Exception as e:
        logging.error(f"Failed to list projects: {e}")
        if logging.getLogger().level == logging.DEBUG:
            logging.exception("Detailed error information:")
        sys.exit(1)


def backup_project(
    domain: str, 
    api_key: str, 
    project_key: str, 
    output_dir: Path,
    backup_issues_flag: bool,
    backup_wiki_flag: bool,
    backup_files_flag: bool,
    backup_git_flag: bool,
    backup_svn_flag: bool
) -> None:
    """Backup a single project.
    
    Args:
        domain: Backlog domain
        api_key: Backlog API key
        project_key: Project key to backup
        output_dir: Output directory
        backup_issues_flag: Whether to backup issues
        backup_wiki_flag: Whether to backup wiki
        backup_files_flag: Whether to backup files
        backup_git_flag: Whether to backup Git repositories
        backup_svn_flag: Whether to backup SVN repositories
    """
    project_output_dir = output_dir / project_key
    project_output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if backup_issues_flag:
            backup_issues(domain, api_key, project_key, project_output_dir)
            
        if backup_wiki_flag:
            backup_wiki(domain, api_key, project_key, project_output_dir)
            
        if backup_files_flag:
            backup_files(domain, api_key, project_key, project_output_dir)
            
        if backup_git_flag:
            backup_git(domain, api_key, project_key, project_output_dir)
            
        if backup_svn_flag:
            backup_svn(domain, api_key, project_key, project_output_dir)
            
        logging.info(f"Backup for project '{project_key}' completed successfully. Files saved to {project_output_dir}")
            
    except Exception as e:
        logging.error(f"Backup for project '{project_key}' failed: {e}")
        if logging.getLogger().level == logging.DEBUG:
            logging.exception("Detailed error information:")


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    args = parse_args()
    setup_logging(args.verbose)
    
    # Get API key from argument or environment variable
    api_key = args.api_key or os.environ.get("BACKLOG_API_KEY")
    if not api_key:
        logging.error("API key must be provided either via --api-key argument or BACKLOG_API_KEY environment variable")
        return 1
        
    # Create Backlog API client
    client = BacklogAPIClient(args.domain, api_key)
    
    # Handle project listing
    if args.list_projects:
        list_projects(
            client, 
            all_projects=args.include_all_space_projects, 
            archived_filter=args.archived_projects
        )
        return 0
        
    # Create output directory if it doesn't exist
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine what to backup
    backup_all = args.all
    backup_issues_flag = backup_all or args.issues
    backup_wiki_flag = backup_all or args.wiki
    backup_files_flag = backup_all or args.files
    backup_git_flag = backup_all or args.git
    backup_svn_flag = backup_all or args.svn
    
    # Handle project-specific or all-projects backup
    try:
        if args.all_projects:
            logging.info("Starting backup for all accessible projects")
            
            # Convert filter choice to API parameter
            archived = None
            if args.archived_projects == "archived-only":
                archived = True
            elif args.archived_projects == "non-archived-only":
                archived = False
                
            projects = client.get_projects(
                all_projects=args.include_all_space_projects,
                archived=archived
            )
            
            for project in projects:
                project_key = project["projectKey"]
                logging.info(f"Starting backup for project: {project_key}")
                backup_project(
                    args.domain,
                    api_key,
                    project_key,
                    output_dir,
                    backup_issues_flag,
                    backup_wiki_flag,
                    backup_files_flag,
                    backup_git_flag,
                    backup_svn_flag
                )
                
            logging.info(f"Backup for all projects completed. Files saved to {output_dir}")
            return 0
            
        elif args.project:
            logging.info(f"Starting Backlog backup for project: {args.project}")
            backup_project(
                args.domain,
                api_key,
                args.project,
                output_dir,
                backup_issues_flag,
                backup_wiki_flag,
                backup_files_flag,
                backup_git_flag,
                backup_svn_flag
            )
            return 0
            
        else:
            logging.error("Either --project, --all-projects, or --list-projects must be specified")
            return 1
            
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        if args.verbose:
            logging.exception("Detailed error information:")
        return 1


if __name__ == "__main__":
    sys.exit(main())