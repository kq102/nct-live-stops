"class for browser"
from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time

class BrowserManager:
    """A class for initializing a browser and driver options"""
    _instance = None
    _lock = Lock()
    _is_shutting_down =False
    _network_responses = []
    _last_used = 0
    BROWSER_TIMEOUT = 300 # 5 MINS

    @classmethod
    def initialize_browser(cls, force_new=False):
        """Initialize Chrome browser for scraping"""
        with cls._lock:
            current_time = time.time()

            # Check if browser needs refresh first
            if (cls._instance and 
                (force_new or current_time - cls._last_used > cls.BROWSER_TIMEOUT)):
                cls.quit_browser()
                cls._instance = None

            if cls._instance is None:
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--silent")
                preferences = {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.default_content_settings.images": 2
                }
                chrome_options.add_experimental_option("prefs", preferences)
                chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
                # chrome_options.binary_location = "/usr/bin/chromium"

                service = Service(executable_path="flask/chromedriver/chromedriver.exe")
                # service = Service(executable_path="/usr/bin/chromedriver")

                cls._instance = webdriver.Chrome(service=service, options=chrome_options)

                # Set shorter timeouts
                cls._instance.set_page_load_timeout(45)
                cls._instance.implicitly_wait(5)

                cls._instance.execute_cdp_cmd('Network.enable',{
                    'maxResourceBufferSize': 1024 * 1024,  # 1MB buffer
                    'maxTotalBufferSize': 1024 * 1024 * 2  # 2MB total
                })
                # Set up network response listener
            cls._last_used = current_time
            return cls._instance


    @classmethod
    def cleanup_session(cls):
        """Cleanup browser session between requests"""
        if cls._instance:
            try:
                cls._instance.execute_cdp_cmd('Network.clearBrowserCache', {})
                cls._instance.execute_script('window.localStorage.clear();')
                cls._instance.execute_script('window.sessionStorage.clear();')
                cls._instance.get_log('performance')  # Clear accumulated logs
            except Exception as e:
                print(f"Session cleanup failed: {e}")
                cls.quit_browser()

    @classmethod
    def get_performance_logs(cls):
        """Get performance logs including network requests"""
        if not cls._instance:
            return []
        
        try:
            logs = []
            for entry in cls._instance.get_log('performance'):
                try:
                    log_data = json.loads(entry['message'])
                    if 'message' in log_data and 'method' in log_data['message']:
                        if log_data['message']['method'] == 'Network.responseReceived':
                            logs.append(log_data)
                except json.JSONDecodeError:
                    continue
            return logs
        except Exception as e:
            print(f"Error getting performance logs: {e}")
            return []
    
    @classmethod
    def quit_browser(cls):
        """Properly quit browser and clean up resources"""
        with cls._lock:
            if cls._instance:
                try:
                    cls._instance.execute_cdp_cmd('Network.disable', {})
                    cls._instance.quit()
                except Exception as e:
                    print(f"Browser quit failed: {e}")
                finally:
                    cls._instance = None