from pydantic import BaseModel
from typing import Union, List


class DonorInfoBase(BaseModel):
    id: int | None = None
    name: str
    age: str
    gender: str
    id_num: str
    sample_type: str
    sample_quantity: str
    date: str
    place: str
    phone: str


class UserBase(BaseModel):
    id: int | None = None
    user_name: str
    authority: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class QueryDateBase(BaseModel):
    start_time: str
    end_time: str


class FuzzyKeywordBase(BaseModel):
    keyword: str
    con: str
