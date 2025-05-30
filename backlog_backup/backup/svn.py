"""SVN repository backup functionality for Backlog."""

import logging
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..api.client import BacklogAPIClient

logger = logging.getLogger(__name__)


def backup_svn(
    client: BacklogAPIClient,
    project_key: str,
    output_dir: Path,
    **kwargs
) -> None:
    """
    Backup SVN repositories from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup SVN repos from
        output_dir: Directory to save backup files
        **kwargs: Additional options
    """
    logger.info(f"Starting SVN backup for project: {project_key}")
    
    try:
        # Create svn directory
        svn_dir = output_dir / "svn"
        svn_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project information
        project = client.get_project(project_key)
        if not project:
            logger.error(f"Project {project_key} not found")
            return
        
        logger.info(f"Found project: {project.get('name', project_key)}")
        
        # Get SVN repositories for the project
        try:
            repositories = client.get_svn_repositories(project_key)
        except Exception as e:
            logger.warning(f"Could not get SVN repositories for project {project_key}: {str(e)}")
            repositories = []
        
        if not repositories:
            logger.warning(f"No SVN repositories found for project {project_key}")
            return
        
        logger.info(f"Found {len(repositories)} SVN repositories to backup")
        
        # Backup each repository
        for repo in repositories:
            repo_name = repo.get('name', f"repo_{repo.get('id', 'unknown')}")
            repo_id = repo.get('id')
            
            try:
                success = _backup_svn_repository(
                    client, 
                    project_key, 
                    repo_name, 
                    repo_id, 
                    svn_dir
                )
                
                if success:
                    logger.info(f"Successfully backed up SVN repository: {repo_name}")
                else:
                    logger.warning(f"Failed to backup SVN repository: {repo_name}")
                    
            except Exception as e:
                logger.error(f"Error backing up SVN repository {repo_name}: {str(e)}")
        
        logger.info(f"SVN backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup SVN repositories for project {project_key}: {str(e)}")
        raise


def _backup_svn_repository(
    client: BacklogAPIClient,
    project_key: str, 
    repo_name: str,
    repo_id: int,
    svn_dir: Path
) -> bool:
    """
    Backup an SVN repository using svn checkout.
    
    Args:
        client: Backlog API client instance
        project_key: Project key
        repo_name: Repository name
        repo_id: Repository ID
        svn_dir: Directory to backup repository into
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Construct repository URL
        # Backlog SVN repository URL format: https://domain/svn/PROJECT_KEY/repo_name
        repo_url = f"https://{client.domain}/svn/{project_key}/{repo_name}"
        
        # Create repository directory
        repo_dir = svn_dir / repo_name
        
        logger.info(f"Checking out SVN repository: {repo_url}")
        
        # Use svn checkout to get the latest version
        # For a full backup, we might want to use svnadmin dump if we had server access
        cmd = [
            "svn", "checkout",
            repo_url,
            str(repo_dir),
            "--username", client.api_key,
            "--password", "",
            "--non-interactive",
            "--trust-server-cert"
        ]
        
        # Run svn checkout command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.debug(f"Successfully checked out SVN repository {repo_name}")
            
            # Also try to get repository info and save it
            _save_svn_info(repo_url, repo_dir, client.api_key)
            
            return True
        else:
            logger.error(f"SVN checkout failed for {repo_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"SVN checkout timeout for repository {repo_name}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error backing up SVN repository {repo_name}: {str(e)}")
        return False


def _save_svn_info(repo_url: str, repo_dir: Path, api_key: str) -> None:
    """Save SVN repository information."""
    try:
        # Get SVN info
        cmd = [
            "svn", "info", repo_url,
            "--username", api_key,
            "--password", "",
            "--non-interactive",
            "--trust-server-cert",
            "--xml"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            info_file = repo_dir / "svn_info.xml"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            logger.debug(f"Saved SVN info to {info_file}")
        
    except Exception as e:
        logger.warning(f"Could not save SVN info: {str(e)}")


def _dump_repository(repo_url: str, output_path: Path, auth_token: Optional[str] = None) -> bool:
    """
    Create an SVN dump of a repository.
    
    Args:
        repo_url: URL of the SVN repository
        output_path: Path where to save the dump file
        auth_token: Authentication token if needed
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # TODO: Implement SVN dump logic
        # This might need to use svnadmin dump or svnsync
        # depending on access permissions
        
        logger.info(f"SVN dump functionality not yet implemented for {repo_url}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error dumping SVN repository {repo_url}: {str(e)}")
        return False
