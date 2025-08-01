from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def initialize_browser():
    """Initialize Chrome browser for scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Path to chrome driver included in project
    service = Service(executable_path="flask/chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Add to initialize_app_data function
def initialize_app_data():
    """initialize_data"""
    print("Initializing app data...")
    browser = initialize_browser()  # Add this line
    print("App data initialization complete")

    return browser
