"""Issue backup functionality for Backlog."""

import json
import csv
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..api.client import BacklogAPIClient

logger = logging.getLogger(__name__)


def backup_issues(
    client: BacklogAPIClient,
    project_key: str,
    output_dir: Path,
    **kwargs
) -> None:
    """
    Backup all issues from a Backlog project.
    
    Args:
        client: Backlog API client instance
        project_key: Project key to backup issues from
        output_dir: Directory to save backup files
        **kwargs: Additional options
    """
    logger.info(f"Starting issue backup for project: {project_key}")
    
    try:
        # Create issues directory
        issues_dir = output_dir / "issues"
        issues_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project information
        project = client.get_project(project_key)
        if not project:
            logger.error(f"Project {project_key} not found")
            return
        
        logger.info(f"Found project: {project.get('name', project_key)}")
        
        # Get all issues for the project
        issues = client.get_issues(project_key)
        
        if not issues:
            logger.warning(f"No issues found for project {project_key}")
            return
        
        logger.info(f"Found {len(issues)} issues to backup")
        
        # Save issue summary as CSV
        csv_file = issues_dir / "issues_summary.csv"
        _save_issues_csv(issues, csv_file)
        logger.info(f"Saved issues summary to {csv_file}")
        
        # Save each issue as individual JSON file
        for issue in issues:
            issue_key = issue.get('issueKey', f"ISSUE-{issue.get('id', 'unknown')}")
            
            # Get detailed issue information (including comments, attachments, etc.)
            detailed_issue = client.get_issue(issue.get('id'))
            if detailed_issue:
                # Save issue details as JSON
                json_file = issues_dir / f"{issue_key}.json"
                _save_issue_json(detailed_issue, json_file)
                logger.debug(f"Saved issue {issue_key} to {json_file}")
                
                # Download attachments if any
                attachments = detailed_issue.get('attachments', [])
                if attachments:
                    _download_issue_attachments(client, issue_key, attachments, issues_dir)
        
        logger.info(f"Issue backup completed for project: {project_key}")
        
    except Exception as e:
        logger.error(f"Failed to backup issues for project {project_key}: {str(e)}")
        raise


def _save_issues_csv(issues: List[Dict[str, Any]], csv_file: Path) -> None:
    """Save issues summary as CSV file."""
    if not issues:
        return
    
    fieldnames = [
        'issueKey', 'summary', 'description', 'status', 'priority', 
        'assignee', 'created', 'updated', 'dueDate', 'estimatedHours', 
        'actualHours', 'issueType', 'category', 'milestone'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for issue in issues:
            row = {}
            for field in fieldnames:
                value = issue.get(field)
                if isinstance(value, dict) and 'name' in value:
                    row[field] = value['name']
                elif isinstance(value, list) and value and isinstance(value[0], dict) and 'name' in value[0]:
                    row[field] = ', '.join([item['name'] for item in value])
                else:
                    row[field] = value
            writer.writerow(row)


def _save_issue_json(issue: Dict[str, Any], json_file: Path) -> None:
    """Save individual issue as JSON file."""
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(issue, f, ensure_ascii=False, indent=2, default=str)


def _download_issue_attachments(
    client: BacklogAPIClient, 
    issue_key: str, 
    attachments: List[Dict[str, Any]], 
    issues_dir: Path
) -> None:
    """Download attachments for an issue."""
    if not attachments:
        return
    
    attachments_dir = issues_dir / "attachments" / issue_key
    attachments_dir.mkdir(parents=True, exist_ok=True)
    
    for attachment in attachments:
        try:
            attachment_id = attachment.get('id')
            filename = attachment.get('name', f'attachment_{attachment_id}')
            
            if attachment_id:
                file_path = attachments_dir / filename
                # Download attachment content as bytes
                content = client.download_attachment(issue_key, str(attachment_id))
                
                # Write content to file
                with open(file_path, 'wb') as f:
                    f.write(content)
                    
                logger.debug(f"Downloaded attachment {filename} for {issue_key}")
                    
        except Exception as e:
            logger.error(f"Error downloading attachment for {issue_key}: {str(e)}")
