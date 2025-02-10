from flaskr.db import Base
from sqlalchemy import Column, Integer, String
class PatologiaModel(Base):
    __tablename__ = "patologia"
    id_patologia = Column(Integer, primary_key=True)
    patologia = Column(String(600), unique=True, nullable=False)

    def __init__(self, patologia):
        self.patologia = patologia

    def __repr__(self):
        return "PatologiaModel(patologia:%s)" % (self.patologia)

    def __json__(self):
        return { 'name': self.patologia }

    # Questo metodo ci permette di ottenere una reference ad una specifica patologia del database
    @classmethod
    def find_patologia(cls, patologia_, session) -> "PatologiaModel":
        result = session.query(cls).filter_by(patologia = patologia_).first()
        return result
    
    # Questo metodo ci permette di riottenere dal database tutte le patologie presenti
    @classmethod
    def get_all_patologie(cls, session):
        result = []
        # Viene eseguito un tentativo per ottenere la lista di patologie
        try:
            patologie = session.query(cls).all()
            for patologia in patologie:
                # Aggiungiamo ad una lista una patologia alla volta
                _ = patologia.patologia
                result.append(patologia)
            
            # Ritorniamo la lista una volta creata
            return result
        # Gestione dell'eccezione
        except Exception:
            {"message": "Internal Server Error."}