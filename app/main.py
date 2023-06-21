from fastapi import FastAPI
import models

from routes import router
from config import engine

from fastapi import Depends, FastAPI

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, prefix="/pokemon", tags=["pokemon"])
