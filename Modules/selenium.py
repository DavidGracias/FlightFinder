from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from fake_useragent import UserAgent



def initializeSelenium():

    
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    # Randomized Chrome Profile:
    ua = UserAgent(browsers=['chrome'])
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    # allows for passwords and signin to work automatically (theoretically)
    chrome_profile = "/Users/davidgracias/Library/Application Support/Google/Chrome/"
    # options.add_argument(f"--user-data-dir={chrome_profile}")

    # Automated options:
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')

    # Mock a non-headless session:
    # options.add_argument('--headless')
    # options.add_argument("--incognito")
    # options.add_argument("--nogpu")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1280,1280")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--enable-javascript")

    # https://www.zenrows.com/blog/selenium-avoid-bot-detection#cloudscraper

    import undetected_chromedriver as uc 
    driver = uc.Chrome()
    return driver

    # # Install cloudscraper with pip install cloudscraper 
    # import cloudscraper 
    
    # # Create cloudscraper instance 
    # scraper = cloudscraper.create_scraper() 
    # # Or: scraper = cloudscraper.CloudScraper() # CloudScraper inherits from requests.Session 
    # print(scraper.get("https://nowsecure.nl").text)

    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    return driver

def main():
    service, driver = initializeSelenium()
    url = "https://www.google.com"
    driver.get(url)