from pydantic import BaseModel, Field

class CardInfo(BaseModel):
    card_code: str = Field(..., title="Card code")
    rarity: str = Field(..., title="Card rarity")
    year: int = Field(..., title="Card year")