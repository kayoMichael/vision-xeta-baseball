from context.setup.extract import Bichette
from context.schemas.card_info import CardInfo
from context.const.prompt import sports_pro_link_extraction_instruction, sports_cards_extract_system_msg, card_info_extract_system_msg, card_info_extract_instruction

import json
from lxml import etree


def baseball_card_services(card_info: CardInfo):
    """Fetch and extract detailed card information from sportscardspro."""

    bichette = Bichette(rate_limit=0, cache=False)

    def fetch_and_clean(url: str) -> str:
        """Fetch a page and return minified HTML as string."""
        tree = bichette.fetch(url)
        html_string = etree.tostring(tree, encoding="unicode", method="html")
        return bichette.minify_html_for_llm(html_string)

    search_url = (
        f"https://www.sportscardspro.com/search-products"
        f"?q={card_info.player_name.replace(' ', '+')}+%23{card_info.card_code}"
        f"&type=prices"
    )

    search_html = fetch_and_clean(search_url)
    search_instruction = sports_pro_link_extraction_instruction(
        f"{card_info.card_year} {card_info.card_name}"
    )

    url_response = bichette.deep_seek(
        prompt=search_html,
        extract_instruction=search_instruction,
        system_msg=sports_cards_extract_system_msg,
    )

    target_url = json.loads(url_response).get("url")
    if not target_url or target_url == "Found None":
        return {"error": "Card not found"}

    card_html = fetch_and_clean(target_url)
    content_response = bichette.deep_seek(
        prompt=card_html,
        extract_instruction=card_info_extract_instruction,
        system_msg=card_info_extract_system_msg,
    )

    return json.loads(content_response)
