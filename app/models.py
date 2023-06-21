from sqlalchemy import Column, Integer, String, Float
from config import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type1 = Column(String)
    type2 = Column(String)
    color = Column(String)
    weight = Column(Float)
    height = Column(Float)
    description = Column(String)
