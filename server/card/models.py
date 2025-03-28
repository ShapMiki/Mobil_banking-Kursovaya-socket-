from sqlalchemy import Column, Integer, String, Double, Computed, Date, ARRAY, DateTime
from modules.database import Base

from datetime import datetime, timedelta



class card(Base):
    __tablename__ = 'card'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
   #owner = relationship(Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)#Счет, копилка, дебитовая карта. кредитная карта
    currency = Column(String, default="byn")
    balance = Column(Integer, default = 0)
    create_at = Column(DateTime, default=Computed(datetime.utcnow()))

    card_number = Column(String, unique=True, nullable=False)
    owner_card = Column(String, default="Incognit")
    valid_to = Column(DateTime, default=Computed(datetime.utcnow()+timedelta(days=365*3)))
    cvv = Column(Integer)
