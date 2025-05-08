import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import trafilatura

def scrape_tutorials(base_url="https://mesozoic-egg.github.io/tinygrad-notes/", output_dir="data/tutorials"):
    os.makedirs(output_dir, exist_ok=True)
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    internal_links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True) if a["href"].startswith("/") or a["href"].startswith(base_url)]
    visited = set()
    for link in internal_links:
        if link not in visited:
            visited.add(link)
            try:
                downloaded = trafilatura.fetch_url(link)
                text_content = trafilatura.extract(downloaded)
                with open(os.path.join(output_dir, f"{link.split('/')[-1]}.txt"), "w") as f:
                    f.write(text_content)
            except Exception as e:
                print(f"Failed to scrape {link}: {e}")
