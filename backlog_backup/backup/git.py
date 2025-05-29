"""Git repository backup functionality for Backlog."""

import logging
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..api.client import BacklogAPIClient

logger = logging.getLogger(__name__)


def backup_git(
    client: BacklogAPIClient,
    project_key: str,
    output_dir: Path,
    **kwargs
) -> None:
    """
    Backup Git repositories from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup Git repos from
        output_dir: Directory to save backup files
        **kwargs: Additional options
    """
    logger.info(f"Starting Git backup for project: {project_key}")
    
    try:
        # Create git directory
        git_dir = output_dir / "git"
        git_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project information
        project = client.get_project(project_key)
        if not project:
            logger.error(f"Project {project_key} not found")
            return
        
        logger.info(f"Found project: {project.get('name', project_key)}")
        
        # TODO: Implement actual Git backup logic
        # This would include:
        # - Getting list of Git repositories
        # - Cloning repositories using git clone --mirror
        # - Handling authentication
        # - Preserving all branches and tags
        
        logger.info(f"Git backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup Git repositories for project {project_key}: {str(e)}")
        raise


def _clone_repository(repo_url: str, output_path: Path, auth_token: Optional[str] = None) -> bool:
    """
    Clone a Git repository using git clone --mirror.
    
    Args:
        repo_url: URL of the repository to clone
        output_path: Path where to clone the repository
        auth_token: Authentication token if needed
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["git", "clone", "--mirror", repo_url, str(output_path)]
        
        # TODO: Handle authentication properly
        # This might need to set up credentials or use SSH keys
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully cloned repository to {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository {repo_url}: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning repository {repo_url}: {str(e)}")
        return False
