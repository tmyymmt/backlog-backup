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
        
        # Get Git repositories for the project
        try:
            repositories = client.get_git_repositories(project_key)
        except Exception as e:
            logger.warning(f"Could not get Git repositories for project {project_key}: {str(e)}")
            repositories = []
        
        if not repositories:
            logger.warning(f"No Git repositories found for project {project_key}")
            return
        
        logger.info(f"Found {len(repositories)} Git repositories to backup")
        
        # Backup each repository
        for repo in repositories:
            repo_name = repo.get('name', f"repo_{repo.get('id', 'unknown')}")
            repo_id = repo.get('id')
            
            try:
                success = _clone_repository(
                    client, 
                    project_key, 
                    repo_name, 
                    repo_id, 
                    git_dir
                )
                
                if success:
                    logger.info(f"Successfully backed up Git repository: {repo_name}")
                else:
                    logger.warning(f"Failed to backup Git repository: {repo_name}")
                    
            except Exception as e:
                logger.error(f"Error backing up Git repository {repo_name}: {str(e)}")
        
        logger.info(f"Git backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup Git repositories for project {project_key}: {str(e)}")
        raise


def _clone_repository(
    client: BacklogAPIClient,
    project_key: str, 
    repo_name: str,
    repo_id: int,
    git_dir: Path
) -> bool:
    """
    Clone a Git repository using git clone --mirror.
    
    Args:
        client: Backlog API client instance
        project_key: Project key
        repo_name: Repository name
        repo_id: Repository ID
        git_dir: Directory to clone repository into
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Construct repository URL
        # Backlog Git repository URL format: https://domain/git/PROJECT_KEY/repo_name.git
        repo_url = f"https://{client.domain}/git/{project_key}/{repo_name}.git"
        
        # Create repository directory
        repo_dir = git_dir / f"{repo_name}.git"
        
        logger.info(f"Cloning Git repository: {repo_url}")
        
        # Use git clone --mirror to create a bare repository backup
        # This preserves all branches, tags, and refs
        cmd = [
            "git", "clone", "--mirror",
            repo_url,
            str(repo_dir)
        ]
        
        # Set up authentication using API key
        env = {
            "GIT_ASKPASS": "echo",
            "GIT_USERNAME": client.api_key,
            "GIT_PASSWORD": "",
        }
        
        # Run git clone command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        if result.returncode == 0:
            logger.debug(f"Successfully cloned repository {repo_name}")
            return True
        else:
            logger.error(f"Git clone failed for {repo_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Git clone timeout for repository {repo_name}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning Git repository {repo_name}: {str(e)}")
        return False
