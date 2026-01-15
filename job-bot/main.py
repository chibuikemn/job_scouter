import json
from scrapers.linkedin import LinkedInScraper
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from matcher.keywords import KeywordMatcher
from sheets.logger import SheetsLogger

def load_config():
    with open('config/requirements.json', 'r') as f:
        return json.load(f)

def scrape_all_platforms(config, matcher, logger):
    total_jobs = 0
    
    # LinkedIn scraping
    if config['platforms']['linkedin']['enabled']:
        linkedin = LinkedInScraper()
        for search_url in config['platforms']['linkedin']['search_urls']:
            print(f"Scraping LinkedIn: {search_url}")
            jobs = linkedin.get_jobs_from_url(search_url)
            total_jobs += process_jobs(jobs, "LinkedIn", matcher, logger, config)
    
    # Greenhouse scraping
    if config['platforms']['greenhouse']['enabled']:
        greenhouse = GreenhouseScraper()
        for company_token in config['platforms']['greenhouse']['company_tokens']:
            print(f"Scraping Greenhouse: {company_token}")
            jobs = greenhouse.get_company_jobs(company_token)
            total_jobs += process_jobs(jobs, "Greenhouse", matcher, logger, config)
    
    # Lever scraping
    if config['platforms']['lever']['enabled']:
        lever = LeverScraper()
        for company_name in config['platforms']['lever']['company_names']:
            print(f"Scraping Lever: {company_name}")
            jobs = lever.get_company_jobs(company_name)
            total_jobs += process_jobs(jobs, "Lever", matcher, logger, config)
    
    return total_jobs

def process_jobs(jobs, platform, matcher, logger, config):
    processed_count = 0
    for job in jobs:
        score = matcher.calculate_score(job.get('content', ''))
        if score >= config['min_match_score']:
            logger.log_job(
                job.get('company', ''),
                job.get('title', ''),
                job.get('url', ''),
                score,
                platform
            )
            processed_count += 1
            print(f"Found match on {platform}: {job.get('title', '')} at {job.get('company', '')} (Score: {score})")
    return processed_count

def main():
    # Load configuration
    config = load_config()
    
    # Initialize matcher
    matcher = KeywordMatcher(config['skills'])
    
    # Initialize logger
    logger = SheetsLogger("credentials.json")
    logger.connect_sheet("Job Applications")
    
    # Scrape all enabled platforms
    total_jobs = scrape_all_platforms(config, matcher, logger)
    
    print(f"\nProcessed {total_jobs} matching jobs across all platforms")

if __name__ == "__main__":
    main()