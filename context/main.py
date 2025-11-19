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
    """Predict rarity and extract OCR info from front/back card images."""
    with open(front_path, "rb") as f1, open(back_path, "rb") as f2:
        result = predict_service(f1.read(), f2.read())
    return result

@mcp.tool()
async def prospect(body: Prospect):
    """Fetch Player Statistics in both Major and Minor League Baseball."""
    try:
        stat = await prospect_info(body)
    except ValueError as e:
        raise e
    return stat

@mcp.tool()
def baseball_card(card_info: CardInfo):
    """Fetch Historical prices of Baseball Cards."""
    try:
        content = baseball_card_services(card_info)
        return content
    except Exception as error:
        raise error

if __name__ == "__main__":
    mcp.run(transport='stdio')