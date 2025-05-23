from F_taste_paziente.db import Base

from sqlalchemy import Column, String, Date, ForeignKey, Integer, LargeBinary, Boolean
from sqlalchemy.orm import relationship, backref


class PazienteModel(Base):
    __tablename__ = 'paziente'

    id_paziente = Column(String(7), primary_key=True)
    data_nascita = Column(Date)
    email = Column(String(45), nullable=False, unique = True)
    password = Column(LargeBinary, nullable=False)
    sesso = Column(Boolean)
    id_nutrizionista = Column(Integer, nullable=True)



    def __init__(self, id_paziente, email, password, data_nascita=None, sesso=None, id_nutrizionista=None):
        self.id_paziente = id_paziente
        self.data_nascita = data_nascita
        self.email = email
        self.password = password
        self.id_nutrizionista = id_nutrizionista
        self.sesso = sesso
        


    def __repr__(self):
        return "PazienteModel(email=%s, id_paziente=%s, password=%s, data_nascita=%s, sesso=%s])" % ( self.email, self.id_paziente, self.password, self.data_nascita, self.sesso)
    
    def __json__(self):
        return { 'id_paziente': self.id_paziente, 'data_nascita': self.data_nascita, 'sesso': self.sesso }
        