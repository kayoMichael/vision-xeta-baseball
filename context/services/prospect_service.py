from context.schemas.prospect import Prospect
from context.support.chadwick_register import ChadwickRegister
from context.setup.extract import Bichette
import json

def prospect_info(prospect: Prospect):
    info = ChadwickRegister(**prospect.model_dump())

    player_id = info.search_player()

    if not player_id:
        raise ValueError(f"Prospect {prospect} not found")

    bichette = Bichette(rate_limit=0, cache=False)
    stat_html = bichette.fetch(f"https://www.baseball-reference.com/players/{player_id[0]}/{player_id}.shtml")
    prompt = bichette.clean_html_for_ai(stat_html)
    statistics = bichette.deep_seek(prompt)

    return json.loads(statistics)
