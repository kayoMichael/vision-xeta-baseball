from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from context.schemas.prospect import Prospect
from context.schemas.card_info import CardInfo

from services.predict_service import predict_service
from services.baseball_card_services import baseball_card_services
from services.prospect_service import prospect_info

mcp = FastMCP("BaseballCardMCP")

@mcp.tool()
def predict_card(front_path: str, back_path: str):
    """
    Predict the Rarity of a baseball card by using the fine-tuned CLIP model and OCR pipeline.

    Use this tool whenever the user provides images of a baseball card (front/back),
    or asks to identify the card, its rarity, parallel, color, numbering,
    autograph status, or surface text.

    :param front_path: Local file path to the card's front image.
    :param back_path: Local file path to the card's back image.
    """

    with open(front_path, "rb") as f1, open(back_path, "rb") as f2:
        result = predict_service(f1.read(), f2.read())
    return result

@mcp.tool()
async def prospect(body: Prospect):
    """
    Fetch detailed MLB and MiLB statistics about a baseball player.

    Use this tool when the user asks about:
    - prospect grades, scouting reports, or minor league stats
    - career statistics, splits, or comparisons
    - Baseball-Reference data

    The birthdate information is optional unless the player has duplicative names with other Major Leaguers.

    :param body: Prospect Information
    :return: Advanced player stats of both Major League and Minor League Performance.
    """
    try:
        stat = await prospect_info(body)
    except ValueError as e:
        raise e
    return stat

@mcp.tool()
def baseball_card(card_info: CardInfo):
    """
    Retrieve pricing data for baseball cards including raw values,
    PSA/BGS grades, recent sales, market trends, and historical charts.

    Use this tool when the user asks for:
    - card values
    - PSA 10 / PSA 9 prices
    - comp sales
    - SportscardsPro or marketplace data

    :param card_info: Baseball Card Information
    :return: Card Pricing Data
    """
    try:
        content = baseball_card_services(card_info)
        return content
    except Exception as error:
        raise error

if __name__ == "__main__":
    mcp.run(transport='stdio')