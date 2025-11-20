from context.support.method import get_current_mlb_season
from openai.types.chat import ChatCompletionSystemMessageParam

prospect_extract_instruction = """
Output ONLY valid JSON following the schema below.

ABSOLUTE RULES (READ CAREFULLY):

1. A player is a TWO-WAY PLAYER (TWP) if they have MLB data as BOTH:
   - a pitcher, AND
   - a batter
   at any point in their career.
   If a player is a TWP, YOU MUST return BOTH batting and pitching stats.
   Do not leave either section null for a TWP.
   Do not return anything unless BOTH batting and pitching stats are filled for a TWP.

2. If a player is NOT a TWP:
   - If the player has ONLY pitching stats → pitching filled, batting = null.
   - If the player has ONLY batting stats → batting filled, pitching = null.

3. The player's listed "position" in the HTML DOES NOT determine whether they are a TWP.
   Use the presence of real batting/pitching statistics to determine if they are a TWP.

4. Follow the schema EXACTLY. No extra fields. No comments. JSON only.

Schema:
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
    "status": "minors (40-man)" | "minors" | "majors" | "retired",
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
    "fielding": {{ "Inn": "float", "PO": "int", "A": "int", "E": "int", "DP": "int", "Fld%": "float", "RF/9": "float",
                   "DRS": "int | null", "OAA": "int | null", "UZR": "float | null", "RngR": "float | null",
                   "ARM": "float | null", "DPR": "float | null", "dWAR": "float | null",
                   "CS%": "float | null", "CFRM": "float | null", "Pos": "string" }}
  }},
  "key_awards": {{
    "MVP": "int", "All Star": "int", "GG": "int", "Platinum Glove": "int", "ML PoY": "int",
    "ERA Title": "int", "Batting title": "int", "Cy Young": "int", "Triple Crown": "int",
    "World Series": "int", "WS MVP": "int", "NLCS MVP": "int", "ALCS MVP": "int", "ROY": "int"
  }}
}}

Do NOT list individual seasons or games.
Set missing fields to null.
For current_year_stats, use the season: {season}
"""

minor_league_prospect_instruction = """
Output ONLY valid JSON. No comments. No text outside JSON. No missing commas. No trailing commas.

READ THESE RULES CAREFULLY:

1. TWO-WAY PLAYER RULE (TWP):
   A player is a TWP if BOTH a Register Pitching TABLE and a Register Batting TABLE exist in the HTML.
   If TWP:
      - You MUST return BOTH batting AND pitching sections for EVERY season.
      - Do NOT return null for either section.
   If NOT TWP:
      - If only pitching table exists → pitching filled, batting = null.
      - If only batting table exists → batting filled, pitching = null.

2. MAJOR LEAGUE ROWS:
   Ignore ALL rows where Lev = "Maj" | "SUMM". Only extract MINOR/Foreign LEAGUE seasons.

3. SEASON OBJECTS:
   For EACH minor league season in the tables:
      - Create a key in the JSON object named "season YEAR", e.g., "season 2022" or "season 2023".
      - Replace YEAR with the actual numeric season from the HTML.
   Do NOT literally output "season xxx".

4. Schema Requirements:
   You must follow the schema EXACTLY.
   Replace all "string", "int", "float" placeholders with REAL extracted values.
   Do NOT include any extra fields not listed in the schema.
   All numeric values must be actual numbers, not quoted placeholders.

5. Output ONLY ONE top-level JSON object containing:
   - "player_profile" { ... }
   - one "season YEAR" object for each Season of minor league. If the player played in different Levels of Minor League in one year. List the aggregate season stats.

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
    "status": "minors (40-man)" | "minors" | "majors" | "retired",
    "draft_info": "string | null"
  }},
  "season YEAR": {{
    "current_league_level": "Rk" | "A-" | "A" | "Fgn" | "A+" | "Fal" | "AA" | "AAA" | "NCAA" if more then one minor league: put them seperated in a slash (e.g A - AA)
    "batting": {{"ba": "float", "hr": "int", "rbi": "int", "h": "int", "obp": "float", "slg": "float", "ops": "int", "tb": "int", "ibb": "int"}} | null,
    "pitching": {{"w": "int", "l": "int", "era": "float", "so": "int", "war": "float", "ip": "float", "whip": "float",
                 "G": "int", "GS": "int", "bb": "int", "GF": "int", "CG": "int", "SV": "int", "SHO": "int", "HBP": "int",
                 "FIP": "float", "SO9": "float", "H9": "float", "HR9": "float", "WP": "int", "SO/BB": "float"}} | null,
  }},
}}
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

baseball_reference_system_msg: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": (
            "You are a data parser that extracts baseball player stats "
            "from Baseball Reference HTML into structured JSON. "
            "Return only valid JSON, with no commentary or explanation."
        ),
    }

ocr_system_msg: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": (
        "You are given OCR-extracted text from a baseball card (front + back). "
    ),
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
