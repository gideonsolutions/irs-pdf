# irs-pdf

Scrapes all PDFs from the [IRS PDF directory](https://www.irs.gov/downloads/irs-pdf) and categorizes them into:

- **forms/** — Tax forms (filenames starting with `f`)
- **instructions/** — Form instructions (filenames starting with `i`)
- **publications/** — IRS publications (filenames starting with `p`)
- **other/** — Everything else

## Usage

```bash
pip install -r requirements.txt
python scrape.py
```

This will:
1. Scrape all 63 pages of the IRS PDF directory
2. Write a `catalog.csv` with every PDF's filename, URL, description, and category
3. Download all PDFs into `pdfs/<category>/`

## Output

- `catalog.csv` — Full catalog of all PDFs with metadata
- `pdfs/forms/` — Downloaded form PDFs
- `pdfs/instructions/` — Downloaded instruction PDFs
- `pdfs/publications/` — Downloaded publication PDFs
- `pdfs/other/` — Uncategorized PDFs
