from flaskr.repositories.nutrizionista_repository import NutrizionistaRepository
from flaskr.models.paziente import PazienteModel
from flaskr.db import get_session

class NutrizionistaService:

    @staticmethod
    def get_nutrizionista_by_paziente(paziente_id):
        session = get_session(role='patient')
        
        paziente = session.get(PazienteModel, paziente_id)
        if not paziente:
            session.close()
            return None

        nutrizionista = NutrizionistaRepository.find_by_id(paziente.fk_nutrizionista, session)
        session.close()

        if not nutrizionista:
            return None

        return nutrizionista
