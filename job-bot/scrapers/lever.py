import requests
from bs4 import BeautifulSoup

class LeverScraper:
    def __init__(self):
        self.api_base = "https://api.lever.co/v0/postings"
    
    def get_company_jobs(self, company_name):
        url = f"{self.api_base}/{company_name}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json()
                result = []
                for job in jobs:
                    description_html = job.get('description', '') + ' ' + job.get('descriptionPlain', '')
                    soup = BeautifulSoup(description_html, 'html.parser')
                    description_text = soup.get_text(separator=' ', strip=True)
                    
                    result.append({
                        'title': job.get('text', ''),
                        'company': company_name,
                        'url': job.get('hostedUrl', ''),
                        'content': description_text
                    })
                return result
        except:
            pass
        return []
    
    def filter_jobs(self, jobs, criteria):
        filtered = []
        for job in jobs:
            if any(skill.lower() in job.get('content', '').lower() for skill in criteria):
                filtered.append(job)
        return filtered