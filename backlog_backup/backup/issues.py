"""Module for backing up Backlog issues."""

import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from ..api.client import BacklogAPIClient


def backup_issues(domain: str, api_key: str, project_key: str, output_dir: Path) -> None:
    """Backup issues for a project.
    
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
    
    logger.info(f"Backing up issues for project {project_key}")
    
    # Create issues directory
    issues_dir = output_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    
    # Create attachments directory
    attachments_dir = issues_dir / "attachments"
    attachments_dir.mkdir(exist_ok=True)
    
    try:
        # Get all issues for the project
        all_issues = []
        count = 100
        offset = 0
        
        while True:
            params = {
                "count": count,
                "offset": offset,
            }
            issues = client.get_issues(project_key, params=params)
            all_issues.extend(issues)
            
            if len(issues) < count:
                break
                
            offset += count
        
        logger.info(f"Found {len(all_issues)} issues")
        
        # Save issue list as CSV
        issue_list_path = issues_dir / "issue_list.csv"
        with open(issue_list_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "id", "issueKey", "summary", "status", "priority", 
                "assignee", "created", "updated", "issue_type"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for issue in all_issues:
                writer.writerow({
                    "id": issue.get("id"),
                    "issueKey": issue.get("issueKey"),
                    "summary": issue.get("summary"),
                    "status": issue.get("status", {}).get("name") if issue.get("status") else "",
                    "priority": issue.get("priority", {}).get("name") if issue.get("priority") else "",
                    "assignee": issue.get("assignee", {}).get("name") if issue.get("assignee") else "",
                    "created": issue.get("created"),
                    "updated": issue.get("updated"),
                    "issue_type": issue.get("issueType", {}).get("name") if issue.get("issueType") else "",
                })
        
        # Save details for each issue
        for issue in all_issues:
            issue_key = issue["issueKey"]
            issue_id = issue["id"]
            
            logger.info(f"Backing up issue {issue_key}")
            
            # Get issue details
            issue_details = client.get_issue(issue_key)
            
            # Get issue comments
            issue_comments = client.get_issue_comments(issue_key)
            
            # Combine issue details with comments
            full_issue_data = {
                "issue": issue_details,
                "comments": issue_comments
            }
            
            # Save issue data as JSON
            issue_file_path = issues_dir / f"{issue_key}.json"
            with open(issue_file_path, "w", encoding="utf-8") as f:
                json.dump(full_issue_data, f, ensure_ascii=False, indent=2)
            
            # Download attachments
            attachments = client.get_issue_attachments(issue_key)
            if attachments:
                issue_attachments_dir = attachments_dir / issue_key
                issue_attachments_dir.mkdir(exist_ok=True)
                
                for attachment in attachments:
                    attachment_id = attachment["id"]
                    attachment_name = attachment["name"]
                    
                    logger.info(f"Downloading attachment {attachment_name} for issue {issue_key}")
                    
                    try:
                        attachment_content = client.download_attachment(issue_key, attachment_id)
                        attachment_path = issue_attachments_dir / attachment_name
                        
                        with open(attachment_path, "wb") as f:
                            f.write(attachment_content)
                    except Exception as attachment_error:
                        logger.warning(f"Failed to download attachment {attachment_name} for issue {issue_key}: {attachment_error}")
                        # Continue with other attachments
        
        logger.info(f"Issues backup completed: {issue_list_path}")
        
    except Exception as e:
        logger.error(f"Failed to backup issues: {e}")
        raise ValueError(f"Issues backup failed: {e}")