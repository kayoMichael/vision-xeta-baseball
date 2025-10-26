from fastapi import APIRouter, File, UploadFile, HTTPException
from context.services.predict_service import predict_service

predict_router = APIRouter()

@predict_router.post("/predict")
async def predict(front: UploadFile = File(...), back: UploadFile = File(...)):
    front_bytes_data = await front.read()
    back_bytes_data = await back.read()
    try:
        result = predict_service(front_bytes_data, back_bytes_data)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return result
