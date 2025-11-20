# Bowman Prospects Classification MCP Server

The value of a Bowman Prospects baseball card is driven almost entirely by two factors:
1. Its rarity (e.g., Atomic, Fuchsia, Shimmer, Gold, etc.) and
2. The player’s current talent level and projected future success in Major League Baseball.
3. The Grading of the Card (PSA 10, PSA 9, ungraded, etc.)

Baseball is one of the most prospect-centric sports in the world. Unlike other sports leagues where teams aggressively trade for established stars or draft picks, MLB organizations routinely stockpile prospects and long-term upside. Because of this, Baseball focuses a lot on prospect development and when they do break out, their Bowman Prospect card can skyrocket in value overnight.

This MCP toolset helps collectors evaluate whether a specific Bowman Prospects card is worth protecting, grading, or holding long-term. It analyzes:
- Card rarity and parallel type
- Player performance profile and breakout potential
- Historical and current market prices across grading tiers
By combining rarity classification, player analytics, and real-time market data, the MCP gives users a clear, data-driven picture of whether their card is a low-upside flip or a high-upside long-term hold worth keeping in pristine condition or even worth grading if its ungraded.

## Available Tools:
- Full Classification of the baseball card from Image using a Fine-Tuned [Clip Model](https://openai.com/index/clip/) (~12,000 datasets) to identify Rarity (chrome, Blue, atomic, etc.), Player on the card, and easyocr to find Grading information as well as and other General Information on the card such as player, code, resume and the year the card was issued.
- Provides Full Career Statistics (Major League and Minor League) including advanced stats such as (WAR, DRS, OPS+, etc.) for full potential and production analysis.
- Provides full pricing data of the card, Volume Sold, for all grading types.

## Sample Workflow

### Input
Consider the Input of paths to these 2 pictures for the Washington Nationals Prospect Hyun-Il Choi. As of Now (Nov 20, 2025), MCP doesn't support directly attaching images into Claude Desktop so we attach file paths for claude to feed. This also ensures Claude can never see the picture and do their own analysis outside of the MCP tool.
<p float="left">
  <img src="https://github.com/user-attachments/assets/399ddadd-20ff-4df5-bf2b-ddc2ac23d4fc" width="200" />
  <img src="https://github.com/user-attachments/assets/a82a5db7-1fce-4616-ab6a-aa0bdfce313b" width="200" />
</p>


### Output
<img width="1512" height="619" alt="Screenshot 2025-11-20 at 12 25 45 AM" src="https://github.com/user-attachments/assets/228a9f69-649d-4324-b228-a9fa04a1d3b1" />
<img width="1511" height="712" alt="Screenshot 2025-11-20 at 12 26 10 AM" src="https://github.com/user-attachments/assets/7ca56fe9-6c6d-437f-a6cd-42c16a32f990" />
<img width="1512" height="574" alt="Screenshot 2025-11-20 at 12 26 24 AM" src="https://github.com/user-attachments/assets/733533c8-1f79-47d4-b921-30f1be15f8e9" />

### Tool Response (Data Given to Claude)
#### Predict
```
{
  "player_profile": {
    "name": "HYUN-IL CHOI",
    "position": "PITCHER",
    "team": "LOS ANGELES DODGERS",
    "date_of_birth": "05-27-2000",
    "location_of_birth": "SEOUL, SOUTH KOREA",
    "resume": "No. 13 Dodgers prospect (Baseball America). Averaged 9.8 SOs/9 IP in 2019 Arizona League, Forged SO/BB ratio of 6.5-to-1 ...Led team in wins (tied), innings and whiffs.",
    "skills": "Varies speeds and locations cunningly to keep hitters guessing: Loose arm action. Low-90s fastball ...Late-breaking hook, . . Promising change-up. Confident athlete.",
    "up_close": "Top contender to go No. 1 overall in Korea Baseball Organization draft coming out of high school. Opted to sign with Dodgers instead"
  },
  "card_info": {
    "card_code": "BCP-130",
    "graded": "Ungraded",
    "serial_number": "Not Numbered",
    "year": 2021,
    "label": "bowman chrome atomic non_auto baseball card"
  }
}
```
#### Prospect
```
{
  "Major League Statistics": null,
  "Minor League Statistics": {
    "player_profile": {
      "name": "Hyun-il Choi",
      "position": "Pitcher",
      "bats": "Right",
      "throws": "Right",
      "height": "6-2",
      "weight": "215lb",
      "birth_date": "May 27, 2000",
      "latest_team": "WSN",
      "status": "minors",
      "draft_info": null
    },
    "season 2019": {
      "current_league_level": "Rk",
      "batting": null,
      "pitching": {
        "w": 5,
        "l": 1,
        "era": 2.63,
        "so": 71,
        "war": null,
        "ip": 65.0,
        "whip": 1.046,
        "G": 14,
        "GS": 11,
        "bb": 11,
        "GF": 0,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 8,
        "FIP": null,
        "SO9": 9.8,
        "H9": 7.9,
        "HR9": 0.8,
        "WP": 2,
        "SO/BB": 6.45
      }
    },
    "season 2021": {
      "current_league_level": "A/A+",
      "batting": null,
      "pitching": {
        "w": 8,
        "l": 6,
        "era": 3.55,
        "so": 106,
        "war": null,
        "ip": 106.1,
        "whip": 0.969,
        "G": 24,
        "GS": 11,
        "bb": 18,
        "GF": 1,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 3,
        "FIP": null,
        "SO9": 9.0,
        "H9": 7.2,
        "HR9": 1.0,
        "WP": 4,
        "SO/BB": 5.89
      }
    },
    "season 2022": {
      "current_league_level": "A+/Rk",
      "batting": null,
      "pitching": {
        "w": 0,
        "l": 1,
        "era": 4.5,
        "so": 4,
        "war": null,
        "ip": 4.0,
        "whip": 1.0,
        "G": 2,
        "GS": 1,
        "bb": 0,
        "GF": 0,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 0,
        "FIP": null,
        "SO9": 9.0,
        "H9": 9.0,
        "HR9": 0.0,
        "WP": 0,
        "SO/BB": null
      }
    },
    "season 2023": {
      "current_league_level": "A+",
      "batting": null,
      "pitching": {
        "w": 4,
        "l": 5,
        "era": 3.75,
        "so": 46,
        "war": null,
        "ip": 60.0,
        "whip": 1.25,
        "G": 16,
        "GS": 13,
        "bb": 12,
        "GF": 0,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 5,
        "FIP": null,
        "SO9": 6.9,
        "H9": 9.5,
        "HR9": 0.9,
        "WP": 2,
        "SO/BB": 3.83
      }
    },
    "season 2024": {
      "current_league_level": "AA/AAA",
      "batting": null,
      "pitching": {
        "w": 5,
        "l": 11,
        "era": 4.92,
        "so": 102,
        "war": null,
        "ip": 115.1,
        "whip": 1.335,
        "G": 24,
        "GS": 21,
        "bb": 40,
        "GF": 2,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 14,
        "FIP": null,
        "SO9": 8.0,
        "H9": 8.9,
        "HR9": 1.0,
        "WP": 1,
        "SO/BB": 2.55
      }
    },
    "season 2025": {
      "current_league_level": "AA/AAA",
      "batting": null,
      "pitching": {
        "w": 7,
        "l": 8,
        "era": 4.87,
        "so": 88,
        "war": null,
        "ip": 116.1,
        "whip": 1.221,
        "G": 30,
        "GS": 20,
        "bb": 34,
        "GF": 1,
        "CG": 0,
        "SV": 0,
        "SHO": 0,
        "HBP": 13,
        "FIP": null,
        "SO9": 6.8,
        "H9": 8.4,
        "HR9": 1.8,
        "WP": 3,
        "SO/BB": 2.59
      }
    }
  }
}
```
### Baseball Card
```
{
  "card_price": {
    "ungraded": "$2.50",
    "grade 1": null,
    "grade 2": null,
    "grade 3": null,
    "grade 4": null,
    "grade 5": null,
    "grade 6": null,
    "grade 7": null,
    "grade 8": null,
    "grade 9": null,
    "grade 9.5": null,
    "TAG 10": null,
    "ACE 10": null,
    "SGC 10": null,
    "CGC 10": null,
    "PSA 10": null,
    "BGS 10": null,
    "BGS 10 Black": null,
    "CGC 10 Pristine": null
  },
  "card_volume": {
    "ungraded sold listings": 5,
    "grade 7 sold listings": 0,
    "grade 8 sold listings": 0,
    "grade 9 sold listings": 0,
    "grade 10 sold listings": 0
  }
}
```

