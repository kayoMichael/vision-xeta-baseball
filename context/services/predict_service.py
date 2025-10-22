from context.image_classification_model.clip_model import ClipModel
from PIL import Image
import io

def predict_service(image):
    clip = ClipModel()
    bytes_data = image.read()
    img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
    clip.predict(img)

