import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver import ChromeOptions, Remote
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.common.exceptions import WebDriverException
import time

load_dotenv()
SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")

def create_driver():
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    return Remote(
        command_executor=SBR_WEBDRIVER,
        options=options
    )

def scrape_website(website):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        driver = None
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            print("Connecting to Scraping Browser...")
            
            driver = create_driver()
            driver.get(website)
            
            print("Waiting for page to load...")
            time.sleep(2)  # Give the page some time to load
            
            print("Checking for captcha...")
            try:
                solve_res = driver.execute(
                    "executeCdpCommand",
                    {
                        "cmd": "Captcha.waitForSolve",
                        "params": {"detectTimeout": 10000},
                    },
                )
                print("Captcha solve status:", solve_res["value"]["status"])
            except WebDriverException as e:
                print("No captcha detected or captcha handling failed:", str(e))
            
            print("Scraping page content...")
            html = driver.page_source
            
            if html and len(html) > 0:
                return html
            else:
                raise Exception("Empty page content received")
                
        except Exception as e:
            print(f"Error during attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to scrape after {max_retries} attempts: {str(e)}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]