from fastapi import HTTPException
from fastapi import APIRouter

from context.schemas.card_info import CardInfo
from context.services.baseball_card_services import baseball_card_services
card_router = APIRouter()

@card_router.get("/baseball_card")
def baseball_card(card_info: CardInfo):
    try:
        content = baseball_card_services(card_info)
        return content
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
