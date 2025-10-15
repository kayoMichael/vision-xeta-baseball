from datetime import datetime

def get_current_mlb_season():
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    if current_month < 5:
        return current_year - 1
    else:
        return current_year