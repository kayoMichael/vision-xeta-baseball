from context.schemas.prospect import Prospect
from context.support.chadwick_register import ChadwickRegister
from context.setup.extract import Bichette
from openai.types.chat import ChatCompletionSystemMessageParam
from context.const.prompt import prospect_instruction
import json

def prospect_info(prospect: Prospect):
    info = ChadwickRegister(**prospect.model_dump())
    player_id = info.search_player()

    if not player_id:
        raise ValueError(f"Prospect {prospect} not found")

    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    system_msg: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": (
            "You are a data parser that extracts baseball player stats "
            "from Baseball Reference HTML into structured JSON. "
            "Return only valid JSON, with no commentary or explanation."
        ),
    }

    bichette = Bichette(rate_limit=0, cache=False, headers=headers)
    stat_html = bichette.fetch(f"https://www.baseball-reference.com/players/{player_id[0]}/{player_id}.shtml")
    prompt = bichette.clean_html_for_ai(stat_html)
    statistics = bichette.deep_seek(prompt=prompt, extract_instruction=prospect_instruction, system_msg=system_msg)

    return json.loads(statistics)
