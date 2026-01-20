import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

class SheetsLogger:
    def __init__(self, credentials_path):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = None
    
    def connect_sheet(self, sheet_name):
        self.sheet = self.client.open(sheet_name).sheet1
    
    def log_job(self, company, role, link, score, platform, status="Not Applied"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sheet.append_row([timestamp, company, role, link, score, platform, status])
        
    def