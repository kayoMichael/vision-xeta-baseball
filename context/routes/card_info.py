from fastapi import APIRouter

router = APIRouter()

@router.get("/baseball_card")
def baseball_card():
    return {"message": "success"}