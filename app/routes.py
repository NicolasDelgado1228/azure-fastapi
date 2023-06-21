from fastapi import APIRouter, HTTPException, Path, status, Depends
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import Request, Response, RequestPokemon, PokemonSchema
from typing import Annotated

from datetime import datetime, timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import redis
import crud


router = APIRouter()

# Redis client
r = redis.Redis(host="localhost", port=6379)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "538a76a7e53a37fa7df0c20ae0431e020e4ec358cec00dfae7d5801202ac9a26"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "nsdr1228": {
        "username": "nsdr1228",
        "full_name": "Nicolás Delgado",
        "email": "nsdr1228@gmail.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/pokemon/token")

# app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


#########################


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create")
async def create_pokemon_service(
    request: RequestPokemon,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        crud.create_pokemon(db, pokemon=request.parameter)
    except Exception as e:
        print(e)

    return Response(
        status="Ok", code="200", message="Pokémon created successfully"
    ).dict(exclude_none=True)


@router.get("/")
async def get_pokemons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _pokemons = crud.get_pokemon(db, skip, limit)
    return Response(
        status="Ok", code="200", message="Success fetch all data", result=_pokemons
    )


@router.patch("/update")
async def update_pokemon(
    request: RequestPokemon,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _pokemon = crud.update_pokemon(
        db,
        pokemon_id=request.parameter.id,
        title=request.parameter.title,
        description=request.parameter.description,
    )
    return Response(
        status="Ok", code="200", message="Success update data", result=_pokemon
    )


@router.delete("/delete")
async def delete_pokemon(
    request: RequestPokemon,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    crud.remove_pokemon(db, pokemon_id=request.parameter.id)
    return Response(status="Ok", code="200", message="Success delete data").dict(
        exclude_none=True
    )


@router.get("/{id}")
async def get_pokemon(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _pokemon = crud.get_pokemon_by_id(db, pokemon_id=id)
    return (
        Response(
            status="Ok", code="200", message="Success get pokemon", result=_pokemon
        )
        if _pokemon
        else HTTPException(status_code=404)
    )
