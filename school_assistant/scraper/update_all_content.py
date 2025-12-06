import subprocess
import sys
from pathlib import Path

# Mapping of section name -> Google Site URL
SECTIONS = {
    "reglements": "https://sites.google.com/eduhainaut.be/apm/outils-enseignant/reglements",
    "documents_utiles": "https://sites.google.com/eduhainaut.be/apm/outils-enseignant/documents-utiles",
    # Add future sections here, e.g. "cabanga": "https://.../cabanga"
}

def run_fetch(section, url):
    """Execute fetch_section.py for a given section.
    The script writes its output to data/<section>.txt.
    """
    script_path = Path(__file__).parents[2] / "scraper" / "fetch_section.py"
    cmd = [sys.executable, str(script_path), url, section]
    print(f"\n=== Scraping {section} ===")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    for name, url in SECTIONS.items():
        run_fetch(name, url)
    print("\n✅ All sections have been scraped. Files are in the data/ folder.")
