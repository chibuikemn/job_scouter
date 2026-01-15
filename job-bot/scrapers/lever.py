import requests

class LeverScraper:
    def __init__(self):
        self.api_base = "https://api.lever.co/v0/postings"
    
    def get_company_jobs(self, company_name):
        url = f"{self.api_base}/{company_name}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json()
                return [{
                    'title': job.get('text', ''),
                    'company': company_name,
                    'url': job.get('hostedUrl', ''),
                    'content': job.get('description', '')
                } for job in jobs]
        except:
            pass
        return []
    
    def filter_jobs(self, jobs, criteria):
        filtered = []
        for job in jobs:
            if any(skill.lower() in job.get('content', '').lower() for skill in criteria):
                filtered.append(job)
        return filtered