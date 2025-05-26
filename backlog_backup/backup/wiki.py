"""Module for backing up Backlog wiki pages."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from ..api.client import BacklogAPIClient


def backup_wiki(domain: str, api_key: str, project_key: str, output_dir: Path) -> None:
    """Backup wiki pages for a project.
    
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
    
    logger.info(f"Backing up wiki pages for project {project_key}")
    
    # Create wiki directory
    wiki_dir = output_dir / "wiki"
    wiki_dir.mkdir(exist_ok=True)
    
    # Create attachments directory
    attachments_dir = wiki_dir / "attachments"
    attachments_dir.mkdir(exist_ok=True)
    
    try:
        # Get all wiki pages for the project
        wiki_pages = client.get_wikis(project_key)
        logger.info(f"Found {len(wiki_pages)} wiki pages")
        
        # Save wiki index
        wiki_index_path = wiki_dir / "wiki_index.json"
        with open(wiki_index_path, "w", encoding="utf-8") as f:
            json.dump(wiki_pages, f, ensure_ascii=False, indent=2)
        
        # Save each wiki page
        for wiki_page in wiki_pages:
            wiki_id = wiki_page["id"]
            wiki_name = wiki_page["name"]
            
            logger.info(f"Backing up wiki page: {wiki_name}")
            
            # Get full wiki page content
            wiki_content = client.get_wiki(wiki_id)
            
            # Save wiki page as JSON
            wiki_file_path = wiki_dir / f"{wiki_name}.json"
            with open(wiki_file_path, "w", encoding="utf-8") as f:
                json.dump(wiki_content, f, ensure_ascii=False, indent=2)
            
            # Save wiki page content as Markdown
            wiki_markdown_path = wiki_dir / f"{wiki_name}.md"
            with open(wiki_markdown_path, "w", encoding="utf-8") as f:
                f.write(wiki_content.get("content", ""))
            
            # Download attachments
            attachments = client.get_wiki_attachments(wiki_id)
            if attachments:
                wiki_attachments_dir = attachments_dir / wiki_name
                wiki_attachments_dir.mkdir(exist_ok=True)
                
                for attachment in attachments:
                    attachment_id = attachment["id"]
                    attachment_name = attachment["name"]
                    
                    logger.info(f"Downloading attachment {attachment_name} for wiki {wiki_name}")
                    
                    attachment_content = client.download_wiki_attachment(wiki_id, attachment_id)
                    attachment_path = wiki_attachments_dir / attachment_name
                    
                    with open(attachment_path, "wb") as f:
                        f.write(attachment_content)
        
        logger.info(f"Wiki backup completed: {wiki_dir}")
        
    except Exception as e:
        logger.error(f"Failed to backup wiki: {e}")
        raise ValueError(f"Wiki backup failed: {e}")