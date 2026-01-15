import requests
from playwright.sync_api import sync_playwright

class GreenhouseScraper:
    def __init__(self):
        self.api_base = "https://boards-api.greenhouse.io/v1/boards"
    
    def get_company_jobs(self, company_token):
        url = f"{self.api_base}/{company_token}/jobs"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('jobs', [])
        return []
    
    def scrape_company_page(self, company_url):
        jobs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(company_url)
            
            page.wait_for_selector("a")
            
            for job_link in page.query_selector_all("a"):
                title = job_link.inner_text()
                link = job_link.get_attribute("href")
                if "job" in link.lower():
                    jobs.append({"title": title, "url": link})
            
            browser.close()
        return jobs