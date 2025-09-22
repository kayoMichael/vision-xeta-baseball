from extract import BaseballInformation


info = BaseballInformation(rate_limit=4.0)

for i in range(2017, 2024):
    url = f"https://www.baseball-reference.com/draft/index.fcgi?year_ID={i}&draft_round=1&draft_type=junreg&query_type=year_round"

    tree = info.fetch(url=url)

    players = info.extract_xpath(tree, "//")
