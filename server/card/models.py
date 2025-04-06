from sqlalchemy import Column, Integer, String, ForeignKey, Double, Computed, Date, ARRAY, DateTime
from sqlalchemy.orm import relationship
from random import randint

from modules.database import Base
from datetime import datetime, timedelta



class Card(Base):
    __tablename__ = 'card'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)

    # Внешний ключ для связи с пользователем
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    type = Column(String, nullable=False)  # Счет, копилка, дебитовая карта, кредитная карта
    currency = Column(String, default="byn")
    balance = Column(Integer, default=0)
    create_at = Column(DateTime, default=datetime.utcnow)

    card_number = Column(String, unique=True, nullable=False)
    owner_card = Column(String, default="Incognit")
    valid_to = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=365*3))
    cvv = Column(Integer)
    pin = Column(Integer, default=randint(1000,9999))

    # Связь "многие к одному" с User
    owner = relationship('User', back_populates='cards')
