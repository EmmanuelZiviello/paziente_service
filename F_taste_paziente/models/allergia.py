from F_taste_paziente.db import Base
from sqlalchemy_utils import StringEncryptedType
from F_taste_paziente.utils.credentials import get_key
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class AllergiaModel(Base):
    __tablename__ = "allergia"
    id_allergia = Column(Integer, primary_key=True)
    allergia = Column(String(600), unique=True, nullable=False)

    def __repr__(self):
        return "AllergiaModel(allergia:%s)" % (self.allergia)

    def __json__(self):
        return { 'name': self.allergia}

    def __init__(self, allergia):
        self.allergia = allergia

    @classmethod
    def find_allergia(cls, allergia_, session) -> "AllergiaModel":
        result = session.query(cls).filter_by(allergia = allergia_).first()
        return result
    
    #Questo metodo ci permette di riottenere dal database tutte le patologie presenti
    @classmethod
    def get_all_allergie(cls, session):
        result = []
        # Viene eseguito un tentativo per ottenere la lista di patologie
        try:
            allergie = session.query(cls).all()
            for allergia in allergie:
                # Aggiungiamo ad una lista una patologia alla volta
                _ = allergia.allergia
                result.append(allergia)
            
            # Ritorniamo la lista una volta creata
            return result
        # Gestione dell'eccezione
        except Exception:
            {"message": "Internal Server Error."}