"""File backup functionality for Backlog."""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..api.client import BacklogAPIClient

logger = logging.getLogger(__name__)


def backup_files(
    client: BacklogAPIClient,
    project_key: str,
    output_dir: Path,
    **kwargs
) -> None:
    """
    Backup all shared files from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup files from
        output_dir: Directory to save backup files
        **kwargs: Additional options
    """
    logger.info(f"Starting file backup for project: {project_key}")
    
    try:
        # Create files directory
        files_dir = output_dir / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project information
        project = client.get_project(project_key)
        if not project:
            logger.error(f"Project {project_key} not found")
            return
        
        logger.info(f"Found project: {project.get('name', project_key)}")
        
        # Recursively backup all files starting from root directory
        _backup_directory(client, project_key, "/", files_dir)
        
        logger.info(f"File backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup files for project {project_key}: {str(e)}")
        raise


def _backup_directory(
    client: BacklogAPIClient,
    project_key: str,
    directory_path: str,
    output_dir: Path
) -> None:
    """
    Recursively backup files from a directory.
    
    Args:
        client: Backlog API client instance
        project_key: Project key
        directory_path: Path to directory in Backlog
        output_dir: Local output directory
    """
    try:
        # Get files and directories in current path
        items = client.get_shared_files(project_key, directory_path)
        
        if not items:
            logger.debug(f"No files found in directory: {directory_path}")
            return
        
        logger.info(f"Found {len(items)} items in directory: {directory_path}")
        
        for item in items:
            item_type = item.get('type')
            item_name = item.get('name', 'unnamed_item')
            item_id = item.get('id')
            
            # Sanitize filename
            safe_name = _sanitize_filename(item_name)
            
            if item_type == 'file':
                # Download file
                try:
                    file_path = output_dir / safe_name
                    content = client.download_shared_file(project_key, str(item_id))
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    # Save file metadata
                    metadata_file = output_dir / f"{safe_name}.metadata.json"
                    _save_file_metadata(item, metadata_file)
                    
                    logger.debug(f"Downloaded file: {item_name}")
                    
                except Exception as e:
                    logger.error(f"Error downloading file {item_name}: {str(e)}")
                    
            elif item_type == 'directory':
                # Create subdirectory and recursively backup
                subdir_path = output_dir / safe_name
                subdir_path.mkdir(parents=True, exist_ok=True)
                
                # Construct new directory path for API call
                new_path = f"{directory_path.rstrip('/')}/{item_name}"
                if directory_path == "/":
                    new_path = f"/{item_name}"
                
                _backup_directory(client, project_key, new_path, subdir_path)
                
    except Exception as e:
        logger.error(f"Error backing up directory {directory_path}: {str(e)}")


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Replace problematic characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    # Limit length
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name or 'unnamed_file'


def _save_file_metadata(item: Dict[str, Any], metadata_file: Path) -> None:
    """Save file metadata as JSON."""
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2, default=str)
