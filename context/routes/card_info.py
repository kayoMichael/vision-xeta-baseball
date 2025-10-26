from fastapi import APIRouter

card_router = APIRouter()

@card_router.get("/baseball_card")
def baseball_card():
    return {"message": "success"}