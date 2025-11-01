import os
from dotenv import load_dotenv
from context.setup.extract import Bichette
from context.const.const import BRAVE_URL

load_dotenv()

BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]
def baseball_card_services(card_name):

    header = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": f"{BRAVE_API_KEY}"
    }
    bichette = Bichette(cache=False, headers=header)
    url = f'{BRAVE_URL}?q={card_name.strip().replace(" ", "+")}'
    result = bichette.fetch(url)

    return result
