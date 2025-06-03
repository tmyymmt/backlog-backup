"""Wiki backup functionality for Backlog."""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..api.client import BacklogAPIClient

logger = logging.getLogger(__name__)


def backup_wiki(
    client: BacklogAPIClient,
    project_key: str,
    output_dir: Path,
    **kwargs
) -> None:
    """
    Backup all wiki pages from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup wiki from
        output_dir: Directory to save backup files
        **kwargs: Additional options
    """
    logger.info(f"Starting wiki backup for project: {project_key}")
    
    try:
        # Create wiki directory
        wiki_dir = output_dir / "wiki"
        wiki_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project information
        project = client.get_project(project_key)
        if not project:
            logger.error(f"Project {project_key} not found")
            return
        
        logger.info(f"Found project: {project.get('name', project_key)}")
        
        # Get all wiki pages for the project
        wiki_pages = client.get_wikis(project_key)
        
        if not wiki_pages:
            logger.warning(f"No wiki pages found for project {project_key}")
            return
        
        logger.info(f"Found {len(wiki_pages)} wiki pages to backup")
        
        # Save each wiki page
        for page in wiki_pages:
            page_id = page.get('id')
            page_name = page.get('name', f'page_{page_id}')
            
            # Sanitize page name for filename
            safe_page_name = _sanitize_filename(page_name)
            
            # Get detailed wiki page content
            detailed_page = client.get_wiki(str(page_id))
            if detailed_page:
                # Save wiki page as JSON
                json_file = wiki_dir / f"{safe_page_name}.json"
                _save_wiki_json(detailed_page, json_file)
                logger.debug(f"Saved wiki page {page_name} to {json_file}")
                
                # Save wiki page content as Markdown file
                md_file = wiki_dir / f"{safe_page_name}.md"
                _save_wiki_markdown(detailed_page, md_file)
                logger.debug(f"Saved wiki page content {page_name} to {md_file}")
                
                # Download wiki attachments if any
                attachments = detailed_page.get('attachments', [])
                if attachments:
                    _download_wiki_attachments(client, safe_page_name, page_id, attachments, wiki_dir)
        
        logger.info(f"Wiki backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup wiki for project {project_key}: {str(e)}")
        raise


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Replace problematic characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    # Limit length
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name or 'unnamed_page'


def _save_wiki_json(page: Dict[str, Any], json_file: Path) -> None:
    """Save individual wiki page as JSON file."""
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(page, f, ensure_ascii=False, indent=2, default=str)


def _save_wiki_markdown(page: Dict[str, Any], md_file: Path) -> None:
    """Save individual wiki page content as Markdown file."""
    content = page.get('content', '')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)


def _download_wiki_attachments(
    client: BacklogAPIClient, 
    page_name: str,
    page_id: int,
    attachments: List[Dict[str, Any]], 
    wiki_dir: Path
) -> None:
    """Download attachments for a wiki page."""
    if not attachments:
        return
    
    attachments_dir = wiki_dir / "attachments" / page_name
    attachments_dir.mkdir(parents=True, exist_ok=True)
    
    for attachment in attachments:
        try:
            attachment_id = attachment.get('id')
            filename = attachment.get('name', f'attachment_{attachment_id}')
            
            if attachment_id:
                file_path = attachments_dir / filename
                # Download attachment content as bytes
                content = client.download_wiki_attachment(str(page_id), str(attachment_id))
                
                # Write content to file
                with open(file_path, 'wb') as f:
                    f.write(content)
                    
                logger.debug(f"Downloaded wiki attachment {filename} for {page_name}")
                    
        except Exception as e:
            logger.error(f"Error downloading wiki attachment for {page_name}: {str(e)}")
