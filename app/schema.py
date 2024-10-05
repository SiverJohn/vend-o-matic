from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Date, Text, Float, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

class Cash(db.Model):
    __tablename__="cash"
    id: Mapped[str] = mapped_column(Text,primary_key=True)
    banked: Mapped[int] = mapped_column(Integer)
    number: Mapped[int] = mapped_column(Integer)
    denomination: Mapped[float] = mapped_column(Float)

class Items(db.Model):
    __tablename__="items"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    sold: Mapped[int] = mapped_column(Integer)
    cost: Mapped[float] = mapped_column(Float)
    inventory: Mapped[int] = mapped_column(Integer)

