import re
import pdfplumber
from context.setup.extract import Bichette
from context.const.baseball_const import BOWMAN_PAPER_PARALLELS_LIST, BOWMAN_CHROME_PARALLELS_LIST


def parse_rows_from_text(text: str):
    """Split extracted PDF text into rows of columns."""
    lines = text.split("\n")
    rows = []

    for line in lines:
        line = line.strip()
        if line:
            columns = re.split(r"\s{2,}", line)
            rows.append(columns)

    return rows


def extract_rows_from_pdf(pdf_path: str):
    """Extract structured rows from specific pages of a Bowman checklist PDF."""
    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(3, 6):  # pages 3–5 (0-indexed)
            if i < len(pdf.pages):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    rows = parse_rows_from_text(text)
                    all_rows.extend(rows)

    return all_rows


def curate_players():
    """Get player codes (BP) from Bowman PDFs and normalize names."""
    player_names = []
    bowman_years = [2018, 2019, 2020, 2021, 2022, 2024, 2025]

    for year in bowman_years:
        rows = extract_rows_from_pdf(f"bowman_checklist/{year}_Bowman.pdf")
        for row in rows:
            if row[0].startswith("BP"):
                if len(row) > 0:
                    row[-1] = row[-1].replace("®", "").replace("™", "")
                player_names.append(row[0])

    return player_names


def generate_player_lists():
    """Return both paper and chrome player lists."""
    player_list = curate_players()
    bowman_player_list = [s.replace("BP", "BCP", 1) for s in player_list]
    return player_list, bowman_player_list


def scrape_ebay(info, player_list, bowman_player_list):
    """Scrape eBay listings for players, saving images into categorized folders."""
    for index, player_group in enumerate([player_list, bowman_player_list]):
        category = "chrome" if index == 1 else "paper"

        for player_name in player_group:
            name = player_name.strip().replace(" ", "+")
            url = (
                f"https://www.ebay.com/sch/i.html?_nkw={name}"
                "&_sacat=0&_from=R40&_trksid=m570.l1313"
                f"&LH_TitleDesc=0&_odkw={name}"
            )
            tree = info.fetch(url=url)
            if not tree:
                raise Exception(f"Could not fetch {name}")

            for item in tree.xpath("//li[contains(@class, 's-card') and starts-with(@id, 'item')]"):
                title = info.extract_xpath(
                    item,
                    ".//div[contains(@class, 's-card__title')]/span[contains(@class, 'primary default')]/text()",
                )[0]
                image_url = info.extract_xpath(
                    item, ".//img[contains(@class, 's-card__image')]/@src"
                )[0]

                matched = None
                if category == "chrome":
                    for parallel in BOWMAN_CHROME_PARALLELS_LIST:
                        if info.has_bowman_parallel(title, parallel):
                            matched = " ".join(parallel)
                            break
                else:
                    for parallel in BOWMAN_PAPER_PARALLELS_LIST:
                        if info.has_parallel(title, parallel):
                            matched = parallel
                            break

                save_dir = f"data_set/{category}/{matched if matched else 'base'}"

                auto = info.has_auto(title)
                safe_name = info.safe_filename(title) + ".jpg"
                info.download_image(image_url, save_dir, safe_name, auto)


def main():
    """Entrypoint for scraping Bowman player images from eBay."""
    info = Bichette(rate_limit=4.0)

    player_list, bowman_player_list = generate_player_lists()

    scrape_ebay(info, player_list, bowman_player_list)


if __name__ == "__main__":
    main()
