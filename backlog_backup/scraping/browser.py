"""Headless browser for scraping Backlog web interface."""

import logging
import time
from typing import Any, Dict, List, Optional
import os
from pathlib import Path
import requests

# Import optional dependencies - will be installed in Dockerfile
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class BacklogBrowser:
    """Headless browser for scraping Backlog web interface with rate limiting."""
    
    def __init__(self, domain: str, username: str, password: str) -> None:
        """Initialize the browser.
        
        Args:
            domain: Backlog domain (e.g., 'example.backlog.com')
            username: Backlog username
            password: Backlog password
        
        Raises:
            ImportError: If Selenium is not installed
            RuntimeError: If browser initialization fails
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium is required for web scraping. "
                "Install it with: pip install selenium"
            )
            
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting - 1 request per second
        self.last_request_time = 0
        self.request_interval = 1.0  # seconds
        
        try:
            self._init_browser()
            self._login()
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            if hasattr(self, "driver"):
                self.driver.quit()
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    def _init_browser(self) -> None:
        """Initialize headless Chrome browser."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)  # seconds
        self.logger.debug("Browser initialized")
    
    def _login(self) -> None:
        """Login to Backlog."""
        login_url = f"{self.base_url}/login"
        self.logger.info(f"Logging in to {login_url}")
        
        self._rate_limited_get(login_url)
        
        try:
            # Find login form and submit credentials
            username_input = self.driver.find_element(By.ID, "loginId")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(self.base_url)
            )
            
            self.logger.info("Login successful")
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error(f"Login failed: {e}")
            raise ValueError(f"Login failed: {e}")
    
    def _rate_limited_get(self, url: str) -> None:
        """Visit URL with rate limiting.
        
        Args:
            url: URL to visit
        """
        # Apply rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_interval:
            sleep_time = self.request_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        # Make the request
        self.logger.debug(f"Visiting {url}")
        self.driver.get(url)
        self.last_request_time = time.time()
    
    def get_project_files(self, project_key: str) -> List[Dict[str, Any]]:
        """Get file tree for a project.
        
        Args:
            project_key: Project key
            
        Returns:
            List of file information
        """
        files_url = f"{self.base_url}/projects/{project_key}/files/tree"
        self._rate_limited_get(files_url)
        
        # Implementation depends on the Backlog file tree structure
        # Note: This implementation may need to be updated based on the actual
        # HTML structure of the Backlog file tree. The selectors and attributes
        # should be verified and adjusted according to the actual HTML.
        
        file_list = []
        try:
            # Wait for file tree to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".file-tree"))
            )
            
            # Extract file information
            # Note: Actual selectors and attributes may vary depending on Backlog's HTML structure
            file_elements = self.driver.find_elements(By.CSS_SELECTOR, ".file-item")
            
            for element in file_elements:
                file_info = {
                    "name": element.get_attribute("data-name"),
                    "path": element.get_attribute("data-path"),
                    "type": element.get_attribute("data-type"),
                }
                file_list.append(file_info)
                
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.warning(f"Failed to extract file tree: {e}")
        
        return file_list
    
    def download_file(self, project_key: str, file_path: str, output_path: str) -> None:
        """Download a file.
        
        Args:
            project_key: Project key
            file_path: Path to file in Backlog
            output_path: Path to save the file
        
        Raises:
            ValueError: If download fails
        """
        import requests
        from pathlib import Path
        
        # Ensure we're logged in for cookie-based auth
        self._ensure_logged_in()
        
        # Get the download URL
        download_url = f"{self.base_url}/downloadFile/{project_key}/{file_path}"
        self.logger.info(f"Downloading file: {download_url}")
        
        # Create parent directories if they don't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get cookies from Selenium session
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            # Download the file using requests with the session cookies
            with requests.get(download_url, cookies=cookies, stream=True, timeout=60) as response:
                response.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            self.logger.info(f"File downloaded successfully to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to download file {file_path}: {e}")
            raise ValueError(f"File download failed: {e}")
    
    def _ensure_logged_in(self) -> None:
        """Ensure we are still logged in, attempt to re-login if needed."""
        # Check if we are logged in by looking for a specific element
        try:
            # Look for an element that indicates we're logged in
            self.driver.find_element(By.CLASS_NAME, "user-icon")
        except NoSuchElementException:
            self.logger.warning("Session expired, re-logging in")
            self._login()
        
    def close(self) -> None:
        """Close the browser."""
        if hasattr(self, "driver"):
            self.driver.quit()
            self.logger.debug("Browser closed")