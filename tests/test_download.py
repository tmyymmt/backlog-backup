"""Tests for download functionality."""

import unittest
from unittest import mock

from backlog_backup.api.client import BacklogAPIClient


class TestDownloadFunctionality(unittest.TestCase):
    """Tests for download functionality in BacklogAPIClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = "example.backlog.com"
        self.api_key = "dummy_api_key"
        self.client = BacklogAPIClient(self.domain, self.api_key)
    
    @mock.patch("backlog_backup.api.client.requests.request")
    def test_download_attachment(self, mock_request):
        """Test downloading an issue attachment."""
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
        """Test downloading a wiki attachment."""
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
    def test_download_wiki_attachment_invalid_response(self, mock_request):
        """Test downloading a wiki attachment with invalid response."""
        # Set up mock with JSON response instead of binary
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        # Call the method and expect an error
        with self.assertRaises(ValueError) as context:
            self.client.download_wiki_attachment("123", "456")
            
        self.assertIn("Expected binary content", str(context.exception))


if __name__ == "__main__":
    unittest.main()