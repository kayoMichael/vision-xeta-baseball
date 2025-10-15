from fastapi import APIRouter, HTTPException
from context.services.prospect_service import prospect_info
from context.schemas.prospect import Prospect

router = APIRouter()

@router.get("/prospect")
def prospect(body: Prospect):
    try:
        stat = prospect_info(body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={e})

    return stat

