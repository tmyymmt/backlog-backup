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
        self.assertEqual(kwargs["url"], f"https://{self.domain}/api/v2/wikis/123/attachments/456")
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)
        self.assertEqual(kwargs["params"]["apiKey"], self.api_key)

if __name__ == "__main__":
    unittest.main()