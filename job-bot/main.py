import json
import threading
from scrapers.linkedin import LinkedInScraper
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from matcher.keywords import KeywordMatcher
from sheets.logger import SheetsLogger

def load_config():
    with open('config/requirements.json', 'r') as f:
        return json.load(f)

def scrape_all_platforms(config, matcher, logger, stop_flag=None):
    if stop_flag is None:
        stop_flag = threading.Event()
    
    total_jobs = 0
    max_jobs = config.get('max_jobs_per_run', 20)
    
    # Count enabled platforms/companies to distribute limit
    company_count = 0
    if config['platforms']['linkedin']['enabled']:
        company_count += len(config['platforms']['linkedin']['search_urls'])
    if config['platforms']['greenhouse']['enabled']:
        company_count += len(config['platforms']['greenhouse']['company_tokens'])
    if config['platforms']['lever']['enabled']:
        company_count += len(config['platforms']['lever']['company_names'])
    
    # Distribute max_jobs across companies (at least 1 per company)
    jobs_per_company = max(1, max_jobs // max(1, company_count)) if company_count > 0 else max_jobs
    remaining_jobs = max_jobs
    
    # LinkedIn scraping
    if config['platforms']['linkedin']['enabled'] and not stop_flag.is_set():
        linkedin = LinkedInScraper()
        for search_url in config['platforms']['linkedin']['search_urls']:
            if stop_flag.is_set():
                break
            print(f"Scraping LinkedIn: {search_url}")
            jobs = linkedin.get_jobs_from_url(search_url)
            processed = process_jobs(jobs, "LinkedIn", matcher, logger, config, jobs_per_company, stop_flag)
            total_jobs += processed
            remaining_jobs -= processed
    
    # Greenhouse scraping
    if config['platforms']['greenhouse']['enabled'] and not stop_flag.is_set():
        greenhouse = GreenhouseScraper()
        for company_token in config['platforms']['greenhouse']['company_tokens']:
            if stop_flag.is_set():
                break
            print(f"Scraping Greenhouse: {company_token}")
            jobs = greenhouse.get_company_jobs(company_token)
            processed = process_jobs(jobs, "Greenhouse", matcher, logger, config, jobs_per_company, stop_flag)
            total_jobs += processed
            remaining_jobs -= processed
    
    # Lever scraping
    if config['platforms']['lever']['enabled'] and not stop_flag.is_set():
        lever = LeverScraper()
        for company_name in config['platforms']['lever']['company_names']:
            if stop_flag.is_set():
                break
            print(f"Scraping Lever: {company_name}")
            jobs = lever.get_company_jobs(company_name)
            processed = process_jobs(jobs, "Lever", matcher, logger, config, jobs_per_company, stop_flag)
            total_jobs += processed
            remaining_jobs -= processed
    
    return total_jobs

def process_jobs(jobs, platform, matcher, logger, config, max_jobs_per_company=None, stop_flag=None):
    if stop_flag is None:
        stop_flag = threading.Event()
    
    processed_count = 0
    job_limit = max_jobs_per_company if max_jobs_per_company else float('inf')
    
    for job in jobs:
        if stop_flag.is_set():
            break
        
        if processed_count >= job_limit:
            print(f"Reached job limit for {platform}")
            break
        
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