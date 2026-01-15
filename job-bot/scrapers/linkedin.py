from playwright.sync_api import sync_playwright

class LinkedInScraper:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
    
    def get_jobs_from_url(self, search_url):
        jobs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(search_url)
            
            page.wait_for_selector(".job-search-card")
            
            for job_card in page.query_selector_all(".job-search-card"):
                title = job_card.query_selector(".base-search-card__title")
                company = job_card.query_selector(".base-search-card__subtitle")
                link = job_card.query_selector("a")
                
                if title and company and link:
                    jobs.append({
                        "title": title.inner_text().strip(),
                        "company": company.inner_text().strip(),
                        "url": link.get_attribute("href")
                    })
            
            browser.close()
        return jobs