from sqlalchemy.orm import Session
from models import Pokemon
from schemas import PokemonSchema


def get_pokemon(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Pokemon).offset(skip).limit(limit).all()


def get_pokemon_by_id(db: Session, pokemon_id: int):
    return db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()


def create_pokemon(db: Session, pokemon: PokemonSchema):
    _pokemon = Pokemon(**pokemon.dict(exclude_none=True))
    db.add(_pokemon)
    db.commit()
    db.refresh(_pokemon)
    return _pokemon


def remove_pokemon(db: Session, pokemon_id: int):
    _pokemon = get_pokemon_by_id(db=db, pokemon_id=pokemon_id)
    db.delete(_pokemon)
    db.commit()


def update_pokemon(db: Session, pokemon_id: int, title: str, description: str):
    _pokemon = get_pokemon_by_id(db=db, pokemon_id=pokemon_id)

    _pokemon.title = title
    _pokemon.description = description

    db.commit()
    db.refresh(_pokemon)
    return _pokemon
