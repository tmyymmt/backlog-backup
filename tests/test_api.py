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
    def test_rate_limit(self, mock_request):
        """Test handling of rate limiting."""
        # First response is rate limited
        rate_limited_response = mock.Mock()
        rate_limited_response.status_code = 429
        rate_limited_response.headers = {"Retry-After": "1"}
        
        # Second response succeeds
        success_response = mock.Mock()
        success_response.status_code = 200
        success_response.headers = {"Content-Type": "application/json"}
        success_response.json.return_value = {"id": 1, "name": "Test"}
        
        mock_request.side_effect = [rate_limited_response, success_response]
        
        with mock.patch("backlog_backup.api.client.time.sleep") as mock_sleep:
            result = self.client.get("/projects")
            
            # Assertions
            self.assertEqual(mock_request.call_count, 2)
            mock_sleep.assert_called_once_with(1)
            self.assertEqual(result, {"id": 1, "name": "Test"})


if __name__ == "__main__":
    unittest.main()