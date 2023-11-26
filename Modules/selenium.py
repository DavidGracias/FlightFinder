from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from fake_useragent import UserAgent



def initializeSelenium():
    # allows for passwords and signin to work automatically (theoretically)
    chrome_profile = "/Users/davidgracias/Library/Application Support/Google/Chrome/"

    ua = UserAgent()
    userAgent = ua.random
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # Mock a non-headless session:
    # options.add_argument('--headless')
    # options.add_argument("--incognito")
    # options.add_argument("--nogpu")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1280,1280")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--enable-javascript")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--disable-blink-features=AutomationControlled')

    # Chrome Profile:
    options.add_argument(f'user-agent={userAgent}')
    # options.add_argument(f"--user-data-dir={chrome_profile}")
    

    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    return service, driver

def main():
    service, driver = initializeSelenium()
    url = "https://www.google.com"
    driver.get(url)