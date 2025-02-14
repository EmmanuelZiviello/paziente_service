from F_taste_paziente.repositories.nutrizionista_repository import NutrizionistaRepository
from F_taste_paziente.repositories.paziente_repository import PazienteRepository
from F_taste_paziente.models.paziente import PazienteModel
from F_taste_paziente.db import get_session

class NutrizionistaService:

    @staticmethod
    def get_nutrizionista_by_paziente(paziente_id):
        session = get_session(role='patient')
        
        paziente = PazienteRepository.find_by_id(paziente_id,session)
        if not paziente:
            session.close()
            return None

        nutrizionista = NutrizionistaRepository.find_by_id(paziente.fk_nutrizionista, session)
        session.close()

        if not nutrizionista:
            return None

        return nutrizionista
