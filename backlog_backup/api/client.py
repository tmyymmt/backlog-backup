"""Backlog API client module."""

import logging
import time
from typing import Any, Dict, List, Optional, Union
import urllib.parse

import requests
from requests.exceptions import RequestException


class BacklogAPIClient:
    """Client for interacting with the Backlog API."""

    def __init__(self, domain: str, api_key: str) -> None:
        """Initialize the Backlog API client.
        
        Args:
            domain: Backlog domain (e.g., 'example.backlog.com')
            api_key: Backlog API key
        """
        self.domain = domain
        self.api_key = api_key
        self.base_url = f"https://{domain}/api/v2"
        self.logger = logging.getLogger(__name__)

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make a request to the Backlog API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            files: Files to upload
            
        Returns:
            API response as JSON
            
        Raises:
            ValueError: If the API returns an error
        """
        # Always include API key in parameters
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        self.logger.debug(f"Making {method} request to {endpoint}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                timeout=60,
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                self.logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data, files)
            
            response.raise_for_status()
            
            # Check if response is JSON
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            return response.content
            
        except RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise ValueError(f"API Error: {error_detail}")
                except (ValueError, KeyError):
                    pass
            raise ValueError(f"API request failed: {e}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a GET request to the Backlog API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response
        """
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send a POST request to the Backlog API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            files: Files to upload
            
        Returns:
            API response
        """
        return self._make_request("POST", endpoint, params=params, data=data, files=files)
    
    def put(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send a PUT request to the Backlog API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            API response
        """
        return self._make_request("PUT", endpoint, params=params, data=data)
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a DELETE request to the Backlog API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response
        """
        return self._make_request("DELETE", endpoint, params=params)
    
    def get_projects(
        self,
        all_projects: bool = False,
        archived: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get list of projects.
        
        Args:
            all_projects: If True, returns all projects in the space (requires admin privileges).
                          If False, returns only projects the user has access to.
            archived: Filter by archive status.
                     If None, returns all projects.
                     If True, returns only archived projects.
                     If False, returns only non-archived projects.
        
        Returns:
            List of project information
        """
        params = {}
        if all_projects:
            params["all"] = "true"
        if archived is not None:
            params["archived"] = str(archived).lower()
            
        return self.get("/projects", params=params)
    
    def get_project(self, project_id_or_key: str) -> Dict[str, Any]:
        """Get project information.
        
        Args:
            project_id_or_key: Project ID or key
            
        Returns:
            Project information
        """
        endpoint = f"/projects/{project_id_or_key}"
        return self.get(endpoint)
    
    def _get_project_id(self, project_key: str) -> int:
        """Get project ID from project key.
        
        Args:
            project_key: Project key
            
        Returns:
            Project ID as integer
        """
        project_info = self.get_project(project_key)
        return project_info["id"]
    
    def get_issues(
        self, 
        project_id_or_key: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get issues in a project.
        
        Args:
            project_id_or_key: Project ID or key
            params: Additional query parameters
            
        Returns:
            List of issues
        """
        if params is None:
            params = {}
        
        # If project_id_or_key is not a number, treat it as a project key and get the ID
        if not project_id_or_key.isdigit():
            project_id = self._get_project_id(project_id_or_key)
        else:
            project_id = int(project_id_or_key)
            
        params["projectId[]"] = project_id
        return self.get("/issues", params=params)
    
    def get_issue(self, issue_id_or_key: str) -> Dict[str, Any]:
        """Get issue details.
        
        Args:
            issue_id_or_key: Issue ID or key
            
        Returns:
            Issue details
        """
        endpoint = f"/issues/{issue_id_or_key}"
        return self.get(endpoint)
    
    def get_issue_comments(
        self, 
        issue_id_or_key: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get issue comments.
        
        Args:
            issue_id_or_key: Issue ID or key
            params: Additional query parameters
            
        Returns:
            List of comments
        """
        endpoint = f"/issues/{issue_id_or_key}/comments"
        return self.get(endpoint, params=params)
    
    def get_issue_attachments(self, issue_id_or_key: str) -> List[Dict[str, Any]]:
        """Get issue attachments.
        
        Args:
            issue_id_or_key: Issue ID or key
            
        Returns:
            List of attachments
        """
        endpoint = f"/issues/{issue_id_or_key}/attachments"
        return self.get(endpoint)
    
    def download_attachment(self, issue_id_or_key: str, attachment_id: str) -> bytes:
        """Download an attachment.
        
        Args:
            issue_id_or_key: Issue ID or key
            attachment_id: Attachment ID
            
        Returns:
            Attachment content as bytes
        """
        endpoint = f"/issues/{issue_id_or_key}/attachments/{attachment_id}/download"
        # Use _make_request directly to handle binary content properly
        response_content = self._make_request("GET", endpoint)
        if isinstance(response_content, bytes):
            return response_content
        else:
            # If it returns a JSON response (error case), raise an error
            raise ValueError(f"Expected binary content for attachment download, got: {type(response_content)}")
    
    def get_wikis(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """Get wiki pages in a project.
        
        Args:
            project_id_or_key: Project ID or key
            
        Returns:
            List of wiki pages
        """
        endpoint = "/wikis"
        params = {"projectId[]": project_id_or_key}
        return self.get(endpoint, params=params)
    
    def get_wiki(self, wiki_id: str) -> Dict[str, Any]:
        """Get wiki page details.
        
        Args:
            wiki_id: Wiki page ID
            
        Returns:
            Wiki page details
        """
        endpoint = f"/wikis/{wiki_id}"
        return self.get(endpoint)
    
    def get_wiki_attachments(self, wiki_id: str) -> List[Dict[str, Any]]:
        """Get wiki page attachments.
        
        Args:
            wiki_id: Wiki page ID
            
        Returns:
            List of attachments
        """
        endpoint = f"/wikis/{wiki_id}/attachments"
        return self.get(endpoint)
    
    def download_wiki_attachment(self, wiki_id: str, attachment_id: str) -> bytes:
        """Download a wiki attachment.
        
        Args:
            wiki_id: Wiki page ID
            attachment_id: Attachment ID
            
        Returns:
            Attachment content
        """
        endpoint = f"/wikis/{wiki_id}/attachments/{attachment_id}/download"
        return self.get(endpoint)
    
    def get_git_repositories(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """Get Git repositories in a project.
        
        Args:
            project_id_or_key: Project ID or key
            
        Returns:
            List of Git repositories
        """
        endpoint = f"/projects/{project_id_or_key}/git/repositories"
        return self.get(endpoint)
    
    def get_svn_repositories(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """Get Subversion repositories in a project.
        
        Args:
            project_id_or_key: Project ID or key
            
        Returns:
            List of Subversion repositories
        """
        endpoint = f"/projects/{project_id_or_key}/svn/repositories"
        return self.get(endpoint)