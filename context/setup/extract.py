import time
import requests_cache
from lxml import html
from pathlib import Path
import requests
import re
import os
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from context.setup.deepseek import DeepSeek
from lxml.html import HtmlElement
from context.const.prompt import prospect_instruction

load_dotenv()
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

class Bichette:
    def __init__(self, rate_limit: float = 1.0, cache: bool = True, headers: dict = None):
        self.rate_limit = rate_limit
        self.session = requests_cache.CachedSession("Skenes") if cache else requests.Session()
        self.headers = headers

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

    @staticmethod
    def extract_xpath(tree, xpath: str):
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

    @staticmethod
    def extract_css(tree, selector: str):
        """Extract list of elements/texts with CSS selector."""
        if tree is None:
            return []
        try:
            results = tree.cssselect(selector)
            return [el.text_content().strip() for el in results if el is not None]
        except Exception as e:
            print(f"CSS selector error: {e}")
            return []

    @staticmethod
    def download_image(img_url, save_dir, filename, auto: bool = False):
        subfolder = "auto" if auto else "non_auto"
        filepath = Path(save_dir) / subfolder / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if filepath.exists():
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
        return re.sub(r'[\\/*?:"<>|#]', "_", name)

    @staticmethod
    def deep_seek(prompt: str) -> str:
        deepseek = DeepSeek()
        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": (
                "You are a data parser that extracts baseball player stats "
                "from Baseball Reference HTML into structured JSON. "
                "Return only valid JSON, with no commentary or explanation."
            ),
        }

        user_msg: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": f"""
        
        {prospect_instruction}
        HTML:
        {prompt}
        """,
        }
        response = deepseek.invoke(system_msg, user_msg)

        try:
            return response
        except Exception as e:
            print(f"DeepSeek request failed: {e}")
            return f"DeepSeek request failed: {e}"

    @staticmethod
    def has_parallel(title, keyword):
        if keyword == "blue":
            return re.search(r"\bblue\b(?!\s+jays)", title.lower()) is not None
        return re.search(rf"\b{keyword}\b", title.lower()) is not None

    @staticmethod
    def clean_html_for_ai(tree: HtmlElement) -> str:
        for bad in tree.xpath("//script|//style|//comment()"):
            bad.getparent().remove(bad)
        html_text = html.tostring(tree, encoding="unicode")
        cutoff_marker = 'data-label="Frequently Asked Questions"'
        idx = html_text.find(cutoff_marker)
        if idx != -1:
            html_text = html_text[:idx]
        html_text = re.sub(r"\s+", " ", html_text)
        return html_text

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