from context.support.method import get_current_mlb_season

instruction = """
You are a data parser that summarizes Baseball Reference HTML into a compact JSON structure.

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

- Summarize season tables into totals.
- Do NOT list every season or game.
- If a field does not exist, set it to null.
- For current_year_stats, list the stats for the player for the season {season}
- Return only valid JSON, no commentary.
"""

schema_instruction = instruction.format(season=get_current_mlb_season())
