from openai import OpenAI
import os
import dotenv
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.chat.completion_create_params import ResponseFormatJSONObject

dotenv.load_dotenv()

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

class DeepSeek:
    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    def invoke(self, system_msg: ChatCompletionSystemMessageParam, user_msg: ChatCompletionUserMessageParam) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            temperature=0,
            response_format=ResponseFormatJSONObject(type="json_object"),
            messages=[system_msg, user_msg],
        )
        return response.choices[0].message.content