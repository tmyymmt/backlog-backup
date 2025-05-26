"""Module for backing up Backlog Git repositories."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from ..api.client import BacklogAPIClient


def backup_git(domain: str, api_key: str, project_key: str, output_dir: Path) -> None:
    """Backup Git repositories for a project.
    
    Args:
        domain: Backlog domain (e.g., 'example.backlog.com')
        api_key: Backlog API key
        project_key: Project key
        output_dir: Output directory for backup files
    
    Raises:
        ValueError: If backup fails
    """
    logger = logging.getLogger(__name__)
    client = BacklogAPIClient(domain, api_key)
    
    logger.info(f"Backing up Git repositories for project {project_key}")
    
    # Create git directory
    git_dir = output_dir / "git"
    git_dir.mkdir(exist_ok=True)
    
    try:
        # Get Git repositories for the project
        repositories = client.get_git_repositories(project_key)
        logger.info(f"Found {len(repositories)} Git repositories")
        
        for repo in repositories:
            repo_name = repo["name"]
            repo_id = repo["id"]
            
            logger.info(f"Backing up Git repository: {repo_name}")
            
            # Repository clone URL (using HTTPS)
            clone_url = f"https://{domain}/git/{project_key}/{repo_name}.git"
            
            # Add API key to URL for authentication
            clone_url_with_auth = f"{clone_url}?apiKey={api_key}"
            
            # Directory for this repository
            repo_dir = git_dir / repo_name
            
            if repo_dir.exists():
                logger.info(f"Repository directory exists, pulling updates: {repo_dir}")
                try:
                    # Pull updates if repo already exists
                    subprocess.run(
                        ["git", "pull", "--all"],
                        cwd=repo_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to pull Git repository: {e}")
                    logger.error(f"Git stderr: {e.stderr}")
                    raise ValueError(f"Git pull failed: {e}")
            else:
                logger.info(f"Cloning Git repository: {clone_url}")
                try:
                    # Clone the repository
                    subprocess.run(
                        ["git", "clone", "--mirror", clone_url_with_auth, repo_dir],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to clone Git repository: {e}")
                    logger.error(f"Git stderr: {e.stderr}")
                    raise ValueError(f"Git clone failed: {e}")
        
        logger.info(f"Git repositories backup completed: {git_dir}")
        
    except Exception as e:
        logger.error(f"Failed to backup Git repositories: {e}")
        raise ValueError(f"Git repositories backup failed: {e}")