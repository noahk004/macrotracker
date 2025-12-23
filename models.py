from pydantic import BaseModel
from datetime import date


class Item(BaseModel):
    name: str
    serving_size: float
    calories: float
    protein: float


class Record(BaseModel):
    date: date
    food: str
    amt: float