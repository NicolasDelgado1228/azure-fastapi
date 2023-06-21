from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from enum import Enum

T = TypeVar("T")


class PokemonTypes(str, Enum):
    fire = "fire"
    bug = "bug"
    dark = "dark"
    dragon = "dragon"
    electric = "electric"
    fairy = "fairy"
    fighting = "fighting"
    flying = "flying"
    ghost = "ghost"
    grass = "grass"
    ice = "ice"
    ground = "ground"
    normal = "normal"
    poison = "poison"
    psychic = "psychic"
    rock = "rock"
    steel = "steel"
    water = "water"


class PokemonSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type1: Optional[PokemonTypes] = None
    type2: Optional[PokemonTypes] = None
    color: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class Request(GenericModel, Generic[T]):
    parameter: Optional[T] = Field(...)


class RequestPokemon(BaseModel):
    parameter: PokemonSchema = Field(...)


class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]
