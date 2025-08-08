"""class for browser"""
from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class BrowserManager:
    """A class for initializing a browser and driver options"""
    _instance = None
    _lock = Lock()
    _is_shutting_down =False

    @classmethod
    def initialize_browser(cls):
        """Initialize Chrome browser for scraping"""
        with cls._lock:
            if cls._instance is None and not cls._is_shutting_down:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                # Path to chrome driver included in project
                service = Service(executable_path="flask/chromedriver/chromedriver.exe")
                cls._instance = webdriver.Chrome(service=service, options=chrome_options)
            return cls._instance

    @classmethod
    def quit_browser(cls):
        """quit the browser"""
        with cls._lock:
            if cls._instance and not cls._is_shutting_down:
                cls._is_shutting_down = True
                try:
                    cls._instance.quit()
                    print("clean!")
                except Exception:
                    pass
                finally:
                    cls._instance = None
                    cls._is_shutting_down = False
