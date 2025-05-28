"""Tests for scraping module."""

import unittest
import os
import tempfile
from unittest import mock
from pathlib import Path

# Import the BacklogBrowser class
from backlog_backup.scraping.browser import BacklogBrowser


class TestBacklogBrowser(unittest.TestCase):
    """Tests for BacklogBrowser."""
    
    @mock.patch('backlog_backup.scraping.browser.BacklogBrowser._init_browser')
    @mock.patch('backlog_backup.scraping.browser.BacklogBrowser._login')
    @mock.patch('requests.get')
    def test_download_file(self, mock_requests_get, mock_login, mock_init_browser):
        """Test the download_file method."""
        # Create a mock for the driver
        mock_driver = mock.Mock()
        
        # Mock cookies
        mock_driver.get_cookies.return_value = [
            {"name": "test_cookie", "value": "test_value"}
        ]
        
        # Mock find_element to make _ensure_logged_in pass
        mock_driver.find_element.return_value = mock.Mock()
        
        # Mock response iter_content to return chunks
        mock_response = mock.Mock()
        mock_response.raise_for_status = mock.Mock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_requests_get.return_value.__enter__.return_value = mock_response
        
        # Create temporary file for test
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "test_file.txt")
            
            # Initialize browser and inject the mock driver
            browser = BacklogBrowser("example.backlog.com", "username", "password")
            browser.driver = mock_driver
            
            # Call the download_file method
            browser.download_file("TEST_PROJECT", "path/to/file.txt", output_path)
            
            # Verify download URL was constructed correctly
            mock_requests_get.assert_called_once()
            args, kwargs = mock_requests_get.call_args
            expected_url = "https://example.backlog.com/downloadFile/TEST_PROJECT/path/to/file.txt"
            self.assertEqual(args[0], expected_url)
            
            # Verify cookies were passed
            self.assertEqual(kwargs["cookies"], {"test_cookie": "test_value"})
            
            # Verify file was written
            with open(output_path, 'rb') as f:
                content = f.read()
                self.assertEqual(content, b"chunk1chunk2")


if __name__ == "__main__":
    unittest.main()