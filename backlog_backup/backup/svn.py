"""Module for backing up Backlog Subversion repositories."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List
import urllib.parse

from ..api.client import BacklogAPIClient


def backup_svn(domain: str, api_key: str, project_key: str, output_dir: Path) -> None:
    """Backup Subversion repositories for a project.
    
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
    
    logger.info(f"Backing up Subversion repositories for project {project_key}")
    
    # Create svn directory
    svn_dir = output_dir / "svn"
    svn_dir.mkdir(exist_ok=True)
    
    try:
        # Get Subversion repositories for the project
        repositories = client.get_svn_repositories(project_key)
        logger.info(f"Found {len(repositories)} Subversion repositories")
        
        for repo in repositories:
            repo_name = repo["name"]
            repo_id = repo["id"]
            
            logger.info(f"Backing up Subversion repository: {repo_name}")
            
            # Repository URL
            repo_url = f"https://{domain}/svn/{project_key}"
            
            # Add API key to URL for authentication
            api_key_param = urllib.parse.quote(api_key)
            repo_url_with_auth = f"{repo_url}?apiKey={api_key_param}"
            
            # Directory for this repository
            repo_dir = svn_dir / repo_name
            
            if repo_dir.exists():
                logger.info(f"Repository directory exists, updating: {repo_dir}")
                try:
                    # Update if repo already exists
                    subprocess.run(
                        ["svn", "update"],
                        cwd=repo_dir,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to update SVN repository: {e}")
                    logger.error(f"SVN stderr: {e.stderr}")
                    raise ValueError(f"SVN update failed: {e}")
            else:
                logger.info(f"Checking out SVN repository: {repo_url}")
                try:
                    # Checkout the repository
                    subprocess.run(
                        ["svn", "checkout", repo_url_with_auth, repo_dir],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to checkout SVN repository: {e}")
                    logger.error(f"SVN stderr: {e.stderr}")
                    raise ValueError(f"SVN checkout failed: {e}")
                    
        logger.info(f"Subversion repositories backup completed: {svn_dir}")
        
    except Exception as e:
        logger.error(f"Failed to backup Subversion repositories: {e}")
        raise ValueError(f"Subversion repositories backup failed: {e}")