from context.image_classification_model.clip_model import ClipModel
from PIL import Image
import io
import json
import easyocr
from context.setup.deepseek import DeepSeek
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from context.const.prompt import card_extract_instruction
reader = easyocr.Reader(['en'])

def predict_service(front, back):
    clip = ClipModel()
    deepseek = DeepSeek()

    front_img = Image.open(io.BytesIO(front)).convert("RGB")
    label = clip.predict(front_img)
    front_results = reader.readtext(front)
    back_results = reader.readtext(back)
    front_text = [t for (_b, t, _c) in front_results]
    back_text = [t for (_b, t, _c) in back_results]

    system_msg: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": (
            "You are given OCR-extracted text from a baseball card (front + back). "
        ),
    }

    user_msg: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": f"""
            {card_extract_instruction}
            Front_card_info:
            {"\n".join(front_text)}
            Back_card_info:
            {"\n".join(back_text)}
            """,
    }
    card_info = deepseek.invoke(system_msg, user_msg)
    output = json.loads(card_info)
    output["card_info"]["label"] = label
    return output
