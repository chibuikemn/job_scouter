# Job Bot

Automated job search and matching system following the blueprint architecture.

## Setup (one-time)

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
   - share the sheet with the service account email (looks like xxx@xxx.iam.gserviceaccount.com)
   P.S: if you skip this it will fail

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

## Sturcture
this is a graphql on how it works:
job-bot/
│
├── main.py                  # Entry point (you run this)
│
├── config/
│   └── requirements.json    # Your job preferences
│
├── scrapers/
│   └── greenhouse.py        # Pulls jobs from Greenhouse sites
│
├── matcher/
│   └── keywords.py          # Scores job vs your skills
│
├── sheets/
│   └── logger.py            # Writes to Google Sheets
│
├── credentials.json         # Google API credentials (DO NOT COMMIT)
│
├── requirements.txt
└── README.md

