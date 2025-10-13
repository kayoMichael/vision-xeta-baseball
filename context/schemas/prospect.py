from pydantic import BaseModel, Field

class Prospect(BaseModel):
    first_name: str = Field(title="The first name of the prospect")
    last_name: str = Field(title="The last name of the prospect")
    birth_year: int | None = Field(default=None, title="The birth year of the prospect")
    birth_month: int | None = Field(default=None, title="The birth month of the prospect")
    birth_day: int | None = Field(default=None, title="The birth day of the prospect")