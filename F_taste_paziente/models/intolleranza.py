from F_taste_paziente.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import StringEncryptedType
from F_taste_paziente.utils.credentials import get_key

class IntolleranzaModel(Base):
    __tablename__ = "intolleranza"
    id_intolleranza = Column(Integer, primary_key=True)
    intolleranza =  Column(String(600), unique=True, nullable=False)

    def __repr__(self):
        return "IntolleranzaModel(intolleranza:%s)" % (self.intolleranza)

    def __json__(self):
        return { 'name': self.intolleranza}

    def __init__(self, intolleranza):
        self.intolleranza = intolleranza

      # Questo metodo ci permette di ottenere una reference ad una specifica patologia del database
    @classmethod
    def find_intolleranza(cls, intolleranza_, session) -> "IntolleranzaModel":
        result = session.query(cls).filter_by(intolleranza = intolleranza_).first()
        return result
    
    # Questo metodo ci permette di riottenere dal database tutte le patologie presenti
    @classmethod
    def get_all_intolleranze(cls, session):
        result = []
        # Viene eseguito un tentativo per ottenere la lista di patologie
        try:
            intolleranze = session.query(cls).all()
            for intolleranza in intolleranze:
                # Aggiungiamo ad una lista una patologia alla volta
                _ = intolleranza.intolleranza
                result.append(intolleranza)
            
            # Ritorniamo la lista una volta creata
            return result
        # Gestione dell'eccezione
        except Exception:
            {"message": "Internal Server Error."}