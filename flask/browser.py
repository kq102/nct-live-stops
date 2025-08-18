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
                try:
                    chrome_options = Options()
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    #ccchrome_options.binary_location = "/usr/bin/chromium"
                    chrome_options.add_argument('--disable-features=TranslateUI')
                    chrome_options.add_argument('--disable-notifications')
                    chrome_options.add_argument('--disable-popup-blocking')
                    chrome_options.page_load_strategy = 'eager'
                    
                    # Set small window size to reduce memory
                    chrome_options.add_argument('--window-size=800,600')
                    # Path to chrome driver included in project
                    #service = Service(executable_path="/usr/bin/chromedriver")
                    service = Service(executable_path="flask/chromedriver/chromedriver.exe")
                    cls._instance = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e:
                    print(f"Failed to initialize browser: {e}")
                    return None
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
