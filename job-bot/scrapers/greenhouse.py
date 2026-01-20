import requests
from bs4 import BeautifulSoup

class GreenhouseScraper:
    def __init__(self):
        self.api_base = "https://boards-api.greenhouse.io/v1/boards"
    
    def get_company_jobs(self, company_token):
        url = f"{self.api_base}/{company_token}/jobs"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json().get('jobs', [])
                result = []
                for job in jobs:
                    job_id = job.get('id')
                    job_detail = self._get_job_detail(company_token, job_id)
                    result.append({
                        'title': job.get('title', ''),
                        'company': company_token,
                        'url': job.get('absolute_url', ''),
                        'content': job_detail
                    })
                return result
        except:
            pass
        return []
    
    def _get_job_detail(self, company_token, job_id):
        url = f"{self.api_base}/{company_token}/jobs/{job_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                job_data = response.json()
                soup = BeautifulSoup(job_data.get('content', ''), 'html.parser')
                return soup.get_text(separator=' ', strip=True)
        except:
            pass
        return ''
    
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