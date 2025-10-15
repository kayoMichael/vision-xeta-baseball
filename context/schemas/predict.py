from pydantic import BaseModel, Field

class Predict(BaseModel):
    image: str = Field(..., title="Image")
    grading: str = Field(..., title="Card Grading")

