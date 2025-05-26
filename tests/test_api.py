"""Tests for API client."""

import unittest
from unittest import mock

from backlog_backup.api.client import BacklogAPIClient


class TestBacklogAPIClient(unittest.TestCase):
    """Tests for BacklogAPIClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = "example.backlog.com"
        self.api_key = "dummy_api_key"
        self.client = BacklogAPIClient(self.domain, self.api_key)
    
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get(self, mock_request):
        """Test the GET method."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get("/projects")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, {"id": 1, "name": "Test"})
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/projects")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
    
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_issues(self, mock_request):
        """Test the get_issues method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "summary": "Test Issue"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_issues("TEST_PROJECT")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "summary": "Test Issue"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/issues")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
        self.assertEqual(kwargs["params"]["projectId[]"], "TEST_PROJECT")
        
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_wikis(self, mock_request):
        """Test the get_wikis method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "name": "Test Wiki"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_wikis("TEST_PROJECT")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "name": "Test Wiki"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/wikis")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
        self.assertEqual(kwargs["params"]["projectId[]"], "TEST_PROJECT")

    @mock.patch("backlog_backup.api.client.requests.request")
    def test_download_attachment(self, mock_request):
        """Test the download_attachment method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.content = b"test attachment content"
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.download_attachment("TEST-1", "123")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, b"test attachment content")
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/issues/TEST-1/attachments/123/download")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_download_wiki_attachment(self, mock_request):
        """Test the download_wiki_attachment method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.content = b"test wiki attachment content"
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.download_wiki_attachment("123", "456")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, b"test wiki attachment content")
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/wikis/123/attachments/456/download")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_projects_default(self, mock_request):
        """Test the get_projects method with default parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "name": "Project 1", "projectKey": "PROJ1"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_projects()
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "name": "Project 1", "projectKey": "PROJ1"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/projects")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
        # No additional parameters should be sent
        self.assertEqual(len(kwargs["params"]), 1)
        
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_projects_with_filters(self, mock_request):
        """Test the get_projects method with filters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "name": "Project 1", "projectKey": "PROJ1"}]
        mock_request.return_value = mock_response
        
        # Call the method with all=True and archived=True
        result = self.client.get_projects(all_projects=True, archived=True)
        
        # Assertions
        self.assertEqual(result, [{"id": 1, "name": "Project 1", "projectKey": "PROJ1"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/projects")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
        self.assertEqual(kwargs["params"]["all"], "true")
        self.assertEqual(kwargs["params"]["archived"], "true")
        
        # Call again with different parameters
        mock_request.reset_mock()
        mock_request.return_value = mock_response
        
        result = self.client.get_projects(all_projects=False, archived=False)
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"].get("all"), None)  # all parameter should not be sent
        self.assertEqual(kwargs["params"]["archived"], "false")
        
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_issue_comments(self, mock_request):
        """Test the get_issue_comments method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "content": "Test Comment"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_issue_comments("TEST-1")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "content": "Test Comment"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/issues/TEST-1/comments")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_git_repositories(self, mock_request):
        """Test the get_git_repositories method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "name": "test-repo"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_git_repositories("TEST_PROJECT")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "name": "test-repo"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/projects/TEST_PROJECT/git/repositories")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_get_svn_repositories(self, mock_request):
        """Test the get_svn_repositories method uses correct parameters."""
        # Set up mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": 1, "name": "test-svn"}]
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_svn_repositories("TEST_PROJECT")
        
        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result, [{"id": 1, "name": "test-svn"}])
        
        # Check the parameters
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/projects/TEST_PROJECT/svn/repositories")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)

if __name__ == "__main__":
    unittest.main()