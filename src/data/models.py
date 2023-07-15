from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    short_desc = Column(String(32), nullable=False)
    long_desc = Column(String(255))
    item_type = Column(ForeignKey('item_type.id'))

class ItemType(Base):
    __tablename__ = 'item_type'
    id = Column(Integer, primary_key=True)
    type_name = Column(String(32), unique=True)
