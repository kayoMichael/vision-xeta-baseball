from fastapi import APIRouter, File, UploadFile, HTTPException
from context.services.predict_service import predict_service
router = APIRouter()

@router.post("/predict")
async def predict(front: UploadFile = File(...), back: UploadFile = File(...)):
    front_bytes_data = await front.read()
    back_bytes_data = await back.read()
    try:
        result = predict_service(front_bytes_data, back_bytes_data)
    except Exception as exception:
        raise HTTPException(status_code=404, detail=str(exception))
    return {"result": result}

