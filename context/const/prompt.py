from context.support.method import get_current_mlb_season
from openai.types.chat import ChatCompletionSystemMessageParam

prospect_extract_instruction = """
Output ONLY valid JSON following this schema exactly:
{{
  "player_profile": {{
    "name": "string",
    "position": "string",
    "bats": "string",
    "throws": "string",
    "height": "string",
    "weight": "string",
    "birth_date": "string",
    "latest_team": "string",
    "status": "minors (40-man)" | "minors" | "majors" | "retired"
    "draft_info": "string | null"
  }},
  "career_totals": {{
    "batting": {{"ba": "float", "hr": "int", "rbi": "int", "war": "float", "h": "int", "obp": "float", "slg": "float", "ops": "int"}} | null,
    "pitching": {{"w": "int", "l": "int", "era": "float", "so": "int", "war": "float", "ip": "float", "whip": "float", "G": "int", "GS": "int"}} | null
  }},
  "current_year_stats": {{
    "batting": {{"ba": "float", "hr": "int", "rbi": "int", "war": "float", "h": "int", "obp": "float", "slg": "float", "ops": "int", "ops+": "int", "tb": "int", "ibb": "int"}} | null,
    "pitching": {{"w": "int", "l": "int", "era": "float", "so": "int", "war": "float", "ip": "float", "whip": "float",
                 "G": "int", "GS": "int", "bb": "int", "GF": "int", "CG": "int", "SV": "int", "SHO": "int", "HBP": "int",
                 "FIP": "float", "SO9": "float", "H9": "float", "HR9": "float", "WP": "int", "SO/BB": "float"}} | null,
    "fielding": {{"Inn": "float", "PO": "int", "A": "int", "E": "int", "DP": "int", "Fld%": "float", "RF/9": "float", "DRS": "int | null", "OAA": "int | null",
                  "UZR": "float | null", "RngR": "float | null", "ARM": "float | null", "DPR": "float | null", "dWAR": "float | null",
                  "CS%": "float | null", "CFRM": "float | null", "Pos": "string"}}
  }},
  "key_awards": {{"MVP": "int", "All Star": "int", "GG": "int", "Platinum Glove": "int", "ML PoY": "int",
                 "ERA Title": "int", "Batting title": "int", "Cy Young": "int", "Triple Crown": "int",
                 "World Series": "int", "WS MVP": "int", "NLCS MVP": "int", "ALCS MVP": "int", "ROY": "int"}}
}}
- Do NOT list every season or game.
- If a field does not exist, set it to null.
- For current_year_stats, list the stats for the player for the season {season}
"""

card_extract_instruction = """
"Return ONLY valid JSON in exactly this structure:"
{
  "player_profile": {
    "name": "string | null",
    "position": "string | null",
    "team": "string | null",
    "date_of_birth": "MM-DD-YYYY | null",
    "location_of_birth": "string | null",
    "resume": "string | null",     // summary paragraph if present
    "skills": "string | null",     // text under a skills/scouting section if present
    "up_close": "string | null"    // text under 'Up Close' or similar header if present
  },
  "card_info": {
    "card_code": "string | null",
    "graded": "PSA/BGS/SGC grading info, or 'Ungraded' if none",
    "serial_number": "string like '/199' | Not Numbered (if none exits)",
    "year": "int" // should be the year after {year}* on the card. This represents the year of issue.
  }
}

Rules:
- Some OCR text may contain typos — infer closest valid interpretation.
- If a field is not findable, return null — do not invent.
- Do not include any fields not listed above.
- Output only JSON. No explanations.
"""


prospect_instruction = prospect_extract_instruction.format(season=get_current_mlb_season())

def sports_pro_link_extraction_instruction(card_label: str) -> str:
    return f"""
    You are given a snippet of HTML containing multiple card listings from sportscardspro.com.
    Each listing includes a card name and its corresponding link (a <a> tag).

    Task:
    - Find the link that belongs to the card whose label or name best matches "{card_label}".
    - If multiple are similar, choose the one that most closely matches the given label.
    - The link is in the format "https://www.sportscardspro.com/game/xxx".

    Output:
    Return a single JSON object in the following format:
    {{
        "url": string
    }}
    """

sports_cards_extract_system_msg: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": (
        "You are a data parser that extracts a valid url from the given html from sportscardspro"
        "Return ONLY ONE valid URL in string format https://www.sportscardspro.com/game/xxx and NOTHING else. ABSOLUTELY NOTHING ELSE"
    ),
}

card_info_extract_system_msg: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": (
        "You are a data parser that extracts a valid url from the given html from sportscardspro"
        "Return Return only valid JSON, with no commentary or explanation."
    )
}

card_info_extract_instruction = """
Output ONLY valid JSON following this schema exactly:
{{
"card_price": {{
    "ungraded": "string | null",
    "grade 1": "string | null",
    "grade 2": "string | null",
    "grade 3": "string | null",
    "grade 4": "string | null",
    "grade 5": "string | null",
    "grade 6": "string | null",
    "grade 7": "string | null",
    "grade 8": "string | null"
    "grade 9": "string | null"
    "grade 9.5": "string | null"
    "TAG 10": "string | null",
    "ACE 10": "string | null",
    "SGC 10": "string | null",
    "CGC 10": "string | null",
    "PSA 10": "string | null",
    "BGS 10": "string | null",
    "BGS 10 Black": "string | null",
    "CGC 10 Pristine": "string | null",
  }},
  "card_volume": {{
    "ungraded sold listings": int,
    "grade 7 sold listings": int,
    "grade 8 sold listings": int,
    "grade 9 sold listings": int,
    "grade 10 sold listings": int,
  }}
}}
"""
