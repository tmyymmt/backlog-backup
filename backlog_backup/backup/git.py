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
    git_username: Optional[str] = None,
    git_password: Optional[str] = None,
    **kwargs
) -> None:
    """
    Backup Git repositories from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup Git repos from
        output_dir: Directory to save backup files
        git_username: Username for Git authentication
        git_password: Password for Git authentication
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
                    git_dir,
                    git_username,
                    git_password
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
    git_dir: Path,
    git_username: Optional[str] = None,
    git_password: Optional[str] = None
) -> bool:
    """
    Clone a Git repository using git clone --mirror.
    
    Args:
        client: Backlog API client instance
        project_key: Project key
        repo_name: Repository name
        repo_id: Repository ID
        git_dir: Directory to clone repository into
        git_username: Username for Git authentication
        git_password: Password for Git authentication
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Construct repository URL
        base_repo_url = f"https://{client.domain}/git/{project_key}/{repo_name}.git"
        
        # Create repository directory
        repo_dir = git_dir / f"{repo_name}.git"
        
        logger.info(f"Cloning Git repository: {repo_name}")
        logger.debug(f"Repository URL: {base_repo_url}")
        
        # Build git clone command
        cmd = ["git", "clone", "--mirror", base_repo_url, str(repo_dir)]
        
        # Set up environment for git
        import os
        env = os.environ.copy()
        env.update({
            "GIT_TERMINAL_PROMPT": "0",  # Disable interactive prompts
        })
        
        # Set up authentication if credentials are provided
        if git_username and git_password:
            # Use credential helper approach for authentication
            import tempfile
            import urllib.parse
            
            # Create temporary credential helper script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"""#!/usr/bin/env python3
import sys
if len(sys.argv) > 1 and sys.argv[1] == 'get':
    print('username={git_username}')
    print('password={git_password}')
""")
                credential_helper = f.name
            
            os.chmod(credential_helper, 0o755)
            
            # Configure git to use our credential helper
            env['GIT_CONFIG_COUNT'] = '1'
            env['GIT_CONFIG_KEY_0'] = 'credential.helper'
            env['GIT_CONFIG_VALUE_0'] = f'!{credential_helper}'
        
        # Run git clone command
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned repository {repo_name}")
                return True
            else:
                logger.error(f"Git clone failed for {repo_name}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
        finally:
            # Clean up credential helper file if it was created
            if git_username and git_password and 'credential_helper' in locals():
                try:
                    os.unlink(credential_helper)
                except OSError:
                    pass
            
    except subprocess.TimeoutExpired:
        logger.error(f"Git clone timeout for repository {repo_name}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning Git repository {repo_name}: {str(e)}")
        return False
