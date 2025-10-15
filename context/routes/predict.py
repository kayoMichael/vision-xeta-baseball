from fastapi import APIRouter
from context.services.predict_service import predict_service
router = APIRouter()

@router.get("/predict")
def predict():
    predict_service()
    return {"message": "success"}

