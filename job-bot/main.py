import json
from scrapers.linkedin import LinkedInScraper
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from matcher.keywords import KeywordMatcher
from sheets.logger import SheetsLogger

def load_config():
    with open('config/requirements.json', 'r') as f:
        return json.load(f)

def main():
    # Load configuration
    config = load_config()
    
    # Initialize matcher
    matcher = KeywordMatcher(config['skills'])
    
    # Initialize logger
    logger = SheetsLogger("credentials.json")
    logger.connect_sheet("Job Applications")
    
    # Initialize scrapers
    greenhouse = GreenhouseScraper()
    
    # Example: scrape jobs and filter by score
    jobs = greenhouse.get_company_jobs("example_company")
    
    for job in jobs:
        score = matcher.calculate_score(job.get('content', ''))
        if score >= config['min_match_score']:
            logger.log_job(
                job.get('company', ''),
                job.get('title', ''),
                job.get('url', ''),
                score
            )
    
    print(f"Processed {len(jobs)} jobs")

if __name__ == "__main__":
    main()