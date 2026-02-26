#!/usr/bin/env python3
"""Scrape all PDF links from the IRS PDF directory and categorize them."""

import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.irs.gov/downloads/irs-pdf"
PDF_BASE = "https://www.irs.gov/pub/irs-pdf/"
TOTAL_PAGES = 63  # pages 0-62
OUTPUT_DIR = "pdfs"


def classify(filename):
    """Classify a PDF filename into form, instruction, publication, or other."""
    name = filename.lower().removesuffix(".pdf")
    if name.startswith("f"):
        return "forms"
    if name.startswith("i"):
        return "instructions"
    if name.startswith("p"):
        return "publications"
    return "other"


def scrape_page(session, page):
    """Scrape a single page of the IRS PDF directory."""
    url = f"{BASE_URL}?page={page}"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    entries = []
    for link in soup.select("a[href$='.pdf']"):
        href = link["href"]
        filename = href.split("/")[-1]
        row = link.find_parent("tr")
        cols = row.find_all("td") if row else []
        description = cols[3].get_text(strip=True) if len(cols) > 3 else ""
        entries.append(
            {
                "filename": filename,
                "url": href,
                "description": description,
                "category": classify(filename),
            }
        )
    return entries


def download_pdf(session, url, dest):
    """Download a PDF file to the given destination."""
    resp = session.get(url, timeout=60, stream=True)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "irs-pdf-scraper/1.0 (educational project)"}
    )

    all_entries = []
    for page in range(TOTAL_PAGES):
        print(f"Scraping page {page + 1}/{TOTAL_PAGES}...")
        entries = scrape_page(session, page)
        all_entries.extend(entries)
        time.sleep(1)  # be polite

    # Write catalog CSV
    with open("catalog.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["filename", "url", "description", "category"]
        )
        writer.writeheader()
        writer.writerows(all_entries)

    counts = {}
    for e in all_entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1

    print(f"\nTotal PDFs found: {len(all_entries)}")
    for cat, count in sorted(counts.items()):
        print(f"  {cat}: {count}")

    # Download PDFs into categorized directories
    for i, entry in enumerate(all_entries, 1):
        dest = os.path.join(OUTPUT_DIR, entry["category"], entry["filename"])
        if os.path.exists(dest):
            continue
        print(f"[{i}/{len(all_entries)}] Downloading {entry['filename']}...")
        try:
            download_pdf(session, entry["url"], dest)
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
