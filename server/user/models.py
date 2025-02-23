from sqlalchemy import Column, Integer, String, Double, Computed, Date, ARRAY
from sqlalchemy.orm import relationship

from modules.database import Base
from association.associations import chat_user_association

from datetime import datetime


class Users(Base):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True, nullable=False)
    name  = Column(String, nullable=False)
    surname = Column(String)
    telephone = Column(String)
    passport_number = Column(String, unique=True)
    passport_id = Column(String, unique=True)
    registered_at = Column(Date , default=datetime.utcnow(), nullable=False)
    last_seance = Column(Date, default=datetime.utcnow(), nullable=False)

    password = Column(String, nullable=False)

    verefy_email = Column(String, default='False', nullable=False)
    verefy_passport = Column(String, default='False', nullable=False)

    ballance = Column(Double, default=0,  nullable=False)
    image = Column(String, default='none_user_photo.jpg')

    cards= relationship('card, secondary=card_user_association, back_populates='owners')

"""class Property(Base):
    __tablename__ = 'property'

    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Double, nullable=False)
    buy_date = Column(Date, nullable=False)
    general_description = Column(String)
"""
