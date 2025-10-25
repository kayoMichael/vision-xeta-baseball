from context.image_classification_model.clip_model import ClipModel
from PIL import Image
import io

def predict_service(front, back):
    clip = ClipModel()
    front_img = Image.open(io.BytesIO(front)).convert("RGB")
    back_img = Image.open(io.BytesIO(back)).convert("RGB")
    label = clip.predict(front_img)
    return label
