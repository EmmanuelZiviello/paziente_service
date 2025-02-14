from F_taste_paziente.db import get_session
from F_taste_paziente.models.nutrizionista import NutrizionistaModel

class NutrizionistaRepository:

  

    @staticmethod
    def find_by_id(id_nutrizionista, session=None):
        session = session or get_session('patient')
        return session.query(NutrizionistaModel).filter_by(id_nutrizionista=id_nutrizionista).first()

    @staticmethod
    def find_by_email(email, session=None):
        session = session or get_session('patient')
        return session.query(NutrizionistaModel).filter_by(email=email).first()

    @staticmethod
    def add(paziente, session=None):
        session = session or get_session('patient')
        session.add(paziente)
        session.commit()

    @staticmethod
    def delete(paziente, session=None):
        session = session or get_session('patient')
        session.delete(paziente)
        session.commit()


   
   
