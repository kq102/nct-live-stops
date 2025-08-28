"class for browser"
from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json

class BrowserManager:
    """A class for initializing a browser and driver options"""
    _instance = None
    _lock = Lock()
    _is_shutting_down =False
    _network_responses = []

    @classmethod
    def initialize_browser(cls):
        """Initialize Chrome browser for scraping"""
        with cls._lock:
            if cls._instance is None and not cls._is_shutting_down:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
                chrome_options.binary_location = "/usr/bin/chromium"

                # service = Service(executable_path="flask/chromedriver/chromedriver.exe")
                service = Service(executable_path="/usr/bin/chromedriver")

                cls._instance = webdriver.Chrome(service=service, options=chrome_options)
                cls._instance.execute_cdp_cmd('Network.enable', {})
                # Set up network response listener

            return cls._instance

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