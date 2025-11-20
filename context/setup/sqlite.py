import sqlite3


def player_setup():
    conn = sqlite3.connect('Skenes.sqlite')

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS baseball_player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            minor_league_id TEXT NOT NULL,
            year_of_birth INTEGER,
            month_of_birth INTEGER,
            day_of_birth INTEGER
        )
    """)
    conn.commit()
    conn.close()

def find_minor_league_id(player_name, year_of_birth=None, month_of_birth=None, day_of_birth=None):
    conn = sqlite3.connect('Skenes.sqlite')
    cursor = conn.cursor()

    query = "SELECT minor_league_id FROM baseball_player WHERE name = ?"
    params = [player_name]

    if year_of_birth is not None:
        query += " AND year_of_birth = ?"
        params.append(year_of_birth)

    if month_of_birth is not None:
        query += " AND month_of_birth = ?"
        params.append(month_of_birth)

    if day_of_birth is not None:
        query += " AND day_of_birth = ?"
        params.append(day_of_birth)

    cursor.execute(query, tuple(params))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def insert_minor_league_id(player_name, minor_league_id, year_of_birth=None, month_of_birth=None, day_of_birth=None):
    conn = sqlite3.connect('Skenes.sqlite')
    cursor = conn.cursor()

    columns = ["name", "minor_league_id"]
    values = [player_name, minor_league_id]
    placeholders = ["?", "?"]

    if year_of_birth is not None:
        columns.append("year_of_birth")
        values.append(year_of_birth)
        placeholders.append("?")

    if month_of_birth is not None:
        columns.append("month_of_birth")
        values.append(month_of_birth)
        placeholders.append("?")

    if day_of_birth is not None:
        columns.append("day_of_birth")
        values.append(day_of_birth)
        placeholders.append("?")

    query = f"""
        INSERT INTO baseball_player ({", ".join(columns)})
        VALUES ({", ".join(placeholders)})
    """

    cursor.execute(query, values)
    conn.commit()
    conn.close()

