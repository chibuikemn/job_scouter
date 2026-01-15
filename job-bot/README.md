# Job Bot

Automated job search and matching system following the blueprint architecture.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

2. Set up Google Sheets:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Download credentials.json
   - Create a sheet named "Job Applications"

3. Configure job criteria in `config/requirements.json`

4. Run: `python main.py`

## MVP Features (Build Order)

✅ Google Sheets logging  
✅ Greenhouse scraping  
✅ Keyword matching  
✅ Score threshold filter  
🔄 LinkedIn read-only ingestion  
🔄 Resume-based embeddings  

## Architecture

Config → Job Sources → Parser/Scraper → Job Matcher → Google Sheets → Review