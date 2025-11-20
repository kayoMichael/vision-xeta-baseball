from context.schemas.prospect import Prospect
from context.support.chadwick_register import ChadwickRegister
from context.setup.extract import Bichette
from context.const.prompt import baseball_reference_system_msg, minor_league_prospect_instruction, prospect_instruction
from context.setup.sqlite import insert_minor_league_id, find_minor_league_id, player_setup
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import json
import asyncio

load_dotenv()
BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]

async def prospect_info(prospect: Prospect):
    player_minor_league_id = find_minor_league_id(player_name=f"{prospect.first_name} {prospect.last_name}", year_of_birth=prospect.birth_year, month_of_birth= prospect.birth_month, day_of_birth=prospect.birth_day)
    bichette = Bichette(rate_limit=0, cache=False)
    if not player_minor_league_id:
        url = "https://api.search.brave.com/res/v1/web/search"

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }

        query = f"{prospect.first_name} {prospect.last_name} Minor League Stats baseball Reference"

        if prospect.birth_month and prospect.birth_day:
            query += f" Born {prospect.birth_year}-{prospect.birth_month}-{prospect.birth_day}"
        elif prospect.birth_year:
            query += f" Born {prospect.birth_year}"

        params = {
            "q": query,
            "count": 20
        }

        minor_bichette = Bichette(rate_limit=0, cache=False, headers=headers, params=params)
        response = minor_bichette.invoke(url)
        data = response.json()
        target_url = None
        if "web" in data and "results" in data["web"]:
            for result in data["web"]["results"]:
                url = result["url"]
                if re.match(r"^https://www\.baseball-reference\.com/register/player\.fcgi\?id=[a-z0-9]+", url):
                    target_url = url
                    break

        if not target_url:
            raise ValueError("No target url found")

        parsed = urlparse(target_url)
        params = parse_qs(parsed.query)
        player_minor_league_id = params["id"][0]
        insert_minor_league_id(f"{prospect.first_name} {prospect.last_name}", player_minor_league_id, prospect.birth_year, prospect.birth_month, prospect.birth_day)

    else:
        target_url = f"https://www.baseball-reference.com/register/player.fcgi?id={player_minor_league_id}"

    minor_league_data = bichette.fetch(target_url)
    minor_league_prompt = bichette.clean_html_for_ai(minor_league_data)
    minor_league_statistics = bichette.deep_seek_async(prompt=minor_league_prompt, extract_instruction=minor_league_prospect_instruction, system_msg=baseball_reference_system_msg)
    info = ChadwickRegister(**prospect.model_dump())
    player_id = info.search_player()
    player_setup()
    major_league_statistics = None
    if player_id:
        major_league_stat_html = bichette.fetch(
            f"https://www.baseball-reference.com/players/{player_id[0]}/{player_id}.shtml")
        prompt = bichette.clean_html_for_ai(major_league_stat_html)
        major_league_statistics = bichette.deep_seek_async(prompt=prompt, extract_instruction=prospect_instruction,
                                                     system_msg=baseball_reference_system_msg)
    res_major, res_minor = await statistic(major_league_statistics, minor_league_statistics)
    if res_major:
        res_major = json.loads(res_major)
    if res_minor:
        res_minor = json.loads(res_minor)
    return {"Major League Statistics": res_major, "Minor League Statistics": res_minor}

async def statistic(major, minor):
    async def none():
        return None

    if not major:
        major = none()
    res_major, res_minor = await asyncio.gather(major, minor)

    return res_major, res_minor
