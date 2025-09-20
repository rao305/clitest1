#!/usr/bin/env python3
"""
HTML scraping script for Purdue CS course data
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os

# Purdue CS data sources
URLS = [
    "https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html",  # Degree requirements
    "https://catalog.purdue.edu/preview_program.php?catoid=7&poid=6557", # Catalog
    "https://www.cs.purdue.edu/academic-programs/courses/2024_fall_courses.html",  # Fall 2024
    "https://www.cs.purdue.edu/academic-programs/courses/2025_fall_courses.html",  # Fall 2025
    "https://www.cs.purdue.edu/academic-programs/courses/2024_spring_courses.html",  # Spring 2024
]

def scrape_course_data():
    """Scrape course information from Purdue CS website"""
    rows = []
    
    for url in URLS:
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for course tables
            for tr in soup.select("tr"):
                cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
                if len(cols) >= 2 and cols[0].startswith("CS"):
                    rows.append({
                        "code": cols[0],
                        "title": cols[1],
                        "credits": cols[2] if len(cols) > 2 else "",
                        "source": url
                    })
            
            # Also look for course information in other formats
            for element in soup.select("p, div, li"):
                text = element.get_text(strip=True)
                if text.startswith("CS ") and "–" in text:
                    parts = text.split("–", 1)
                    if len(parts) == 2:
                        code_part = parts[0].strip()
                        title_part = parts[1].strip()
                        rows.append({
                            "code": code_part,
                            "title": title_part,
                            "credits": "",
                            "source": url
                        })
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Create output directory
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["code", "title"])
    df.to_csv("data/courses_html.csv", index=False)
    
    print(f"Scraped {len(df)} course entries")
    return df

if __name__ == "__main__":
    scrape_course_data()