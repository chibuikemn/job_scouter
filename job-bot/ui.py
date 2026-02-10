import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
from main import scrape_all_platforms
from matcher.keywords import KeywordMatcher
from sheets.logger import SheetsLogger

class JobScouterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scouter")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Stop mechanism
        self.stop_search_flag = threading.Event()
        self.search_thread = None
        
        # Create main scrollable frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Use scrollable_frame for all widgets
        # Platform Selection
        platform_frame = ttk.LabelFrame(scrollable_frame, text="Platforms", padding=10)
        platform_frame.pack(fill="x", padx=10, pady=5)
        
        self.linkedin_var = tk.BooleanVar(value=False)
        self.greenhouse_var = tk.BooleanVar(value=True)
        self.lever_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(platform_frame, text="LinkedIn", variable=self.linkedin_var).pack(anchor="w")
        ttk.Checkbutton(platform_frame, text="Greenhouse", variable=self.greenhouse_var).pack(anchor="w")
        ttk.Checkbutton(platform_frame, text="Lever", variable=self.lever_var).pack(anchor="w")
        
        # Job Titles
        titles_frame = ttk.LabelFrame(scrollable_frame, text="Job Titles (comma-separated)", padding=10)
        titles_frame.pack(fill="x", padx=10, pady=5)
        self.titles_entry = scrolledtext.ScrolledText(titles_frame, height=3)
        self.titles_entry.pack(fill="x")
        self.titles_entry.insert("1.0", "Software Engineer, Data Analyst, Backend Engineer")
        
        # Skills
        skills_frame = ttk.LabelFrame(scrollable_frame, text="Skills (comma-separated)", padding=10)
        skills_frame.pack(fill="x", padx=10, pady=5)
        self.skills_entry = scrolledtext.ScrolledText(skills_frame, height=3)
        self.skills_entry.pack(fill="x")
        self.skills_entry.insert("1.0", "Python, Java, SQL, JavaScript")
        
        # Locations
        locations_frame = ttk.LabelFrame(scrollable_frame, text="Locations (comma-separated)", padding=10)
        locations_frame.pack(fill="x", padx=10, pady=5)
        self.locations_entry = scrolledtext.ScrolledText(locations_frame, height=2)
        self.locations_entry.pack(fill="x")
        self.locations_entry.insert("1.0", "Remote, United States")
        
        # Min Match Score
        score_frame = ttk.LabelFrame(scrollable_frame, text="Minimum Match Score", padding=10)
        score_frame.pack(fill="x", padx=10, pady=5)
        self.score_var = tk.DoubleVar(value=0.35)
        ttk.Scale(score_frame, from_=0.0, to=1.0, variable=self.score_var, orient="horizontal").pack(fill="x")
        self.score_label = ttk.Label(score_frame, text="0.35")
        self.score_label.pack()
        self.score_var.trace_add("write", lambda *args: self.score_label.config(text=f"{self.score_var.get():.2f}"))
        
        # Max Jobs Limit
        limit_frame = ttk.LabelFrame(scrollable_frame, text="Max Jobs Per Run (distributed across companies)", padding=10)
        limit_frame.pack(fill="x", padx=10, pady=5)
        self.max_jobs_var = tk.IntVar(value=20)
        ttk.Scale(limit_frame, from_=5, to=100, variable=self.max_jobs_var, orient="horizontal").pack(fill="x")
        self.limit_label = ttk.Label(limit_frame, text="20 jobs total")
        self.limit_label.pack()
        self.max_jobs_var.trace_add("write", lambda *args: self.limit_label.config(text=f"{int(self.max_jobs_var.get())} jobs total"))
        
        # Company Inputs
        company_frame = ttk.LabelFrame(scrollable_frame, text="Company Tokens/Names (comma-separated)", padding=10)
        company_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(company_frame, text="Greenhouse Companies:").pack(anchor="w")
        self.greenhouse_entry = ttk.Entry(company_frame)
        self.greenhouse_entry.pack(fill="x", pady=2)
        self.greenhouse_entry.insert(0, "stripe, airbnb, coinbase")
        
        ttk.Label(company_frame, text="Lever Companies:").pack(anchor="w")
        self.lever_entry = ttk.Entry(company_frame)
        self.lever_entry.pack(fill="x", pady=2)
        self.lever_entry.insert(0, "spotify, robinhood, databricks")
        
        # Run Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Job Search", command=self.start_search_thread)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop Search", command=self.stop_search, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Output Log
        log_frame = ttk.LabelFrame(scrollable_frame, text="Search Log", padding=10)
        log_frame.pack(fill="both", padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state="disabled")
        self.log_text.pack(fill="both")
    
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()
    
    def start_search_thread(self):
        """Start job search in a background thread"""
        self.stop_search_flag.clear()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.search_thread = threading.Thread(target=self.run_search, daemon=True)
        self.search_thread.start()
    
    def stop_search(self):
        """Set flag to stop the search"""
        self.log("\n⏹ Stopping search...")
        self.stop_search_flag.set()
        self.stop_button.config(state="disabled")
    
    def run_search(self):
        try:
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.config(state="disabled")
            
            config = {
                "titles": [t.strip() for t in self.titles_entry.get("1.0", "end").strip().split(",")],
                "skills": [s.strip() for s in self.skills_entry.get("1.0", "end").strip().split(",")],
                "locations": [l.strip() for l in self.locations_entry.get("1.0", "end").strip().split(",")],
                "min_match_score": self.score_var.get(),
                "max_jobs_per_run": int(self.max_jobs_var.get()),
                "platforms": {
                    "linkedin": {"enabled": self.linkedin_var.get(), "search_urls": []},
                    "greenhouse": {
                        "enabled": self.greenhouse_var.get(),
                        "company_tokens": [c.strip() for c in self.greenhouse_entry.get().split(",") if c.strip()]
                    },
                    "lever": {
                        "enabled": self.lever_var.get(),
                        "company_names": [c.strip() for c in self.lever_entry.get().split(",") if c.strip()]
                    }
                }
            }
            
            self.log("Initializing job search...")
            matcher = KeywordMatcher(config['skills'])
            logger = SheetsLogger("credentials.json")
            logger.connect_sheet("Job Applications")
            
            self.log("Starting scrape...")
            total_jobs = scrape_all_platforms(config, matcher, logger, self.stop_search_flag)
            
            if self.stop_search_flag.is_set():
                self.log(f"\n⏹ Search stopped by user. Found {total_jobs} matching jobs.")
                messagebox.showinfo("Stopped", f"Search stopped. Found {total_jobs} matching jobs!")
            else:
                self.log(f"\n✓ Search complete! Found {total_jobs} matching jobs.")
                messagebox.showinfo("Success", f"Found {total_jobs} matching jobs!")
            
        except Exception as e:
            self.log(f"\n✗ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            # Re-enable start button
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.stop_button.config(state="disabled"))

def main():
    root = tk.Tk()
    app = JobScouterUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
