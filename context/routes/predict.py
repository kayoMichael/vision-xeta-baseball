from context.main import mcp
from context.services.predict_service import predict_service

@mcp.tool()
def predict_card(front_path: str, back_path: str):
    """Predict rarity and extract OCR info from front/back card images."""
    with open(front_path, "rb") as f1, open(back_path, "rb") as f2:
        result = predict_service(f1.read(), f2.read())
    return result
