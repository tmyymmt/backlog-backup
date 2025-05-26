"""Module for backing up Backlog files."""

import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from ..api.client import BacklogAPIClient
from ..scraping.browser import BacklogBrowser


def backup_files(
    domain: str, 
    api_key: str, 
    project_key: str, 
    output_dir: Path,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> None:
    """Backup files for a project.
    
    Args:
        domain: Backlog domain (e.g., 'example.backlog.com')
        api_key: Backlog API key
        project_key: Project key
        output_dir: Output directory for backup files
        username: Optional Backlog username for web scraping
        password: Optional Backlog password for web scraping
    
    Raises:
        ValueError: If backup fails
    """
    logger = logging.getLogger(__name__)
    
    # Create files directory
    files_dir = output_dir / "files"
    files_dir.mkdir(exist_ok=True)
    
    logger.info(f"Backing up files for project {project_key}")
    
    # Files API is limited in Backlog, so we need to use both API and scraping
    client = BacklogAPIClient(domain, api_key)
    
    try:
        # First try using API if available
        try:
            # Note: This is a placeholder - Backlog API doesn't have a direct
            # method to list all files. You may need to adapt based on
            # what's available in the Backlog API.
            logger.info("Attempting to backup files using API")
            # Implement API-based file backup here if available
            
        except Exception as api_error:
            logger.warning(f"API-based file backup failed: {api_error}")
            logger.info("Falling back to web scraping for files")
            
            if not username or not password:
                raise ValueError(
                    "Username and password are required for web scraping files. "
                    "Please provide them using the --username and --password options."
                )
                
            # Use web scraping as a fallback
            browser = None
            try:
                browser = BacklogBrowser(domain, username, password)
                file_list = browser.get_project_files(project_key)
                
                for file_info in file_list:
                    file_path = file_info["path"]
                    file_name = file_info["name"]
                    file_type = file_info["type"]
                    
                    # Create directory structure if needed
                    path_parts = file_path.split("/")
                    if len(path_parts) > 1:
                        dir_path = files_dir / "/".join(path_parts[:-1])
                        dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Download file if it's not a directory
                    if file_type != "directory":
                        output_path = files_dir / file_path
                        logger.info(f"Downloading file: {file_path}")
                        browser.download_file(project_key, file_path, output_path)
                        
                        # Rate limiting
                        time.sleep(1)
                
            finally:
                if browser:
                    browser.close()
        
        logger.info(f"Files backup completed: {files_dir}")
        
    except Exception as e:
        logger.error(f"Failed to backup files: {e}")
        raise ValueError(f"Files backup failed: {e}")