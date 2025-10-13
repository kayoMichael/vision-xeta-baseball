from fastapi import APIRouter, HTTPException
from context.services.prospect_service import prospect_info
from context.schemas.prospect import Prospect

router = APIRouter()

@router.get("/prospect")
def prospect(body: Prospect):
    prospect = prospect_info(body)

    return prospect

