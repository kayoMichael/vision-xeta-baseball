from dataclasses import dataclass, field
from typing import Optional
import os
import pandas as pd

from ..const.const import REPO_URL, CHADWICK_CONTENT_URL
import requests

@dataclass
class ChadwickRegister:
    first_name: str
    last_name: str
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    __construction: bool = field(init=False, default=False)
    __datafiles: list[str] = field(init=False, default=None)

    def __post_init__(self):
        if "data" not in os.listdir(os.curdir) or "players.csv" not in os.listdir("./data"):
            self.__construction = True


    def search_player(self):
        frames = []
        if self.__construction:
            try:
                response = requests.get(REPO_URL, params={"recursive": "1"})
                response.raise_for_status()
                resource = response.json()["tree"]
                data_files = [file["path"] for file in resource if file["path"].startswith("data/people") and file["type"] == "blob"]

                for file in data_files:
                    df = pd.read_csv(f'{CHADWICK_CONTENT_URL}/{file}', low_memory=False)
                    if "key_bbref" in df.columns:
                        df = df[df["key_bbref"].notna()]
                        cols_to_keep = [c for c in ["key_bbref", "name_first", "name_last", "birth_year", "birth_month", "birth_day"] if c in df.columns]
                        df = df[cols_to_keep]
                        frames.append(df)

                combined_df = pd.concat(frames, ignore_index=True)
                os.makedirs('./data', exist_ok=True)
                combined_df.to_csv("./data/players.csv", index=False)
            except requests.exceptions.HTTPError as e:
                print(f"Error with fetching chadwick register data: {e}")

        df = pd.read_csv("./data/players.csv", low_memory=False)

        match = df[
            (df["name_first"].str.strip().str.lower() == self.first_name.lower().strip()) &
            (df["name_last"].str.strip().str.lower() == self.last_name.lower().strip())
        ]

        external = [
            ("birth_year", self.birth_year),
            ("birth_month", self.birth_month),
            ("birth_day", self.birth_day)
        ]

        index = 0
        while len(match) > 1 and index < len(external):
            col, val = external[index]
            if val is not None:
                match = match[match[col].astype("Int64") == int(val)]
            index += 1

        if len(match) == 1:
            return match.iloc[0]["key_bbref"]
        else:
            return None
