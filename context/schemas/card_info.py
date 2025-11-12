from pydantic import BaseModel, Field

class CardInfo(BaseModel):
    card_code: str = Field(..., title="Card code")
    rarity: str = Field(..., title="Card rarity")
    player_name: str = Field(..., title="Player name")
    card_name: str = Field(..., title="Card name")
    card_year: int | None = Field(..., title="Card year")
