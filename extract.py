import time
import requests
from lxml import html

class BaseballInformation:
    def __init__(self, rate_limit: float = 1.0, user_agent: str = None):
        self.rate_limit = rate_limit
        self.headers = {
            "User-Agent": user_agent
            or "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch(self, url: str):
        """Fetch a URL and return lxml HTML tree."""
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            r.raise_for_status()
            time.sleep(self.rate_limit)
            return html.fromstring(r.content)
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
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
            print(f"[!] CSS selector error: {e}")
            return []
