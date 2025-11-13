from context.main import mcp
from context.schemas.card_info import CardInfo
from context.services.baseball_card_services import baseball_card_services

@mcp.tool()
def baseball_card(card_info: CardInfo):
    try:
        content = baseball_card_services(card_info)
        return content
    except Exception as error:
        raise error
