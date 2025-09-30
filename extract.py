import time
import requests_cache
from lxml import html
from pathlib import Path
import requests
import re

class Bichette:
    def __init__(self, rate_limit: float = 1.0, user_agent: str = None):
        self.rate_limit = rate_limit
        self.session = requests_cache.CachedSession("Skenes")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def fetch(self, url: str):
        """Fetch a URL and return lxml HTML tree."""
        try:
            r = self.session.get(url, headers=self.headers)
            r.raise_for_status()

            if not getattr(r, 'from_cache', False):
                print(f"Fresh request for {url}, sleeping {self.rate_limit}s")
                time.sleep(self.rate_limit)
            else:
                print(f"Cache hit for {url}")

            return html.fromstring(r.content)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_xpath(self, tree, xpath: str):
        """Extract list of elements/texts with XPath."""
        if tree is None:
            return []
        try:
            results = tree.xpath(xpath)
            return [r.strip() if isinstance(r, str) else r.text_content().strip()
                    for r in results if r is not None]
        except Exception as e:
            print(f"[!] XPath error: {e}")
            return []

    def extract_css(self, tree, selector: str):
        """Extract list of elements/texts with CSS selector."""
        if tree is None:
            return []
        try:
            results = tree.cssselect(selector)
            return [el.text_content().strip() for el in results if el is not None]
        except Exception as e:
            print(f"CSS selector error: {e}")
            return []

    def download_image(self, img_url, save_dir, filename, auto: bool = False):
        subfolder = "auto" if auto else "non_auto"
        filepath = Path(save_dir) / subfolder / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if filepath.exists():
            print(f"Skipping: {filepath}")
            return filepath
        try:
            r = requests.get(img_url, timeout=10)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)
            return filepath
        except Exception as e:
            print(f"[!] Failed to download {img_url}: {e}")
            return None

    @staticmethod
    def safe_filename(name: str) -> str:
        # Replace illegal chars with underscores
        return re.sub(r'[\\/*?:"<>|#]', "_", name)

    @staticmethod
    def has_parallel(title, keyword):
        if keyword == "blue":
            return re.search(r"\bblue\b(?!\s+jays)", title.lower()) is not None
        return re.search(rf"\b{keyword}\b", title.lower()) is not None

    @staticmethod
    def has_bowman_parallel(title, keyword: list[str]):
        if len(keyword) == 1 and keyword[0] == "blue":
            return re.search(r"\bblue\b(?!\s+jays)", title.lower()) is not None
        return all(re.search(rf"\b{word}\b", title.lower()) for word in keyword)

    @staticmethod
    def has_auto(title: str) -> bool:
        title_lower = title.lower()
        keywords = [
            r"\bauto\b",
            r"\bautograph\b",
            r"\bsigned\b",
            r"\bsignature\b",
            r"\bcertified auto\b"
        ]
        for pattern in keywords:
            if re.search(pattern, title_lower):
                return True
        return False