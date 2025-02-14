from F_taste_paziente.repositories.nutrizionista_repository import NutrizionistaRepository
from F_taste_paziente.repositories.paziente_repository import PazienteRepository
from F_taste_paziente.models.paziente import PazienteModel
from F_taste_paziente.schemas.nutrizionista import NutrizionistaSchema
from F_taste_paziente.db import get_session

nutrizionista_schema_for_dump = NutrizionistaSchema(only=['id_nutrizionista', 'nome', 'cognome'])



class NutrizionistaService:

    @staticmethod
    def get_nutrizionista_by_paziente(paziente_id):
        session = get_session(role='patient')
        
        paziente = PazienteRepository.find_by_id(paziente_id,session)
        if not paziente:
            session.close()
            return {"message":"Paziente non trovato"},400

        nutrizionista = NutrizionistaRepository.find_by_id(paziente.fk_nutrizionista, session)

        if not nutrizionista:
            return {"message":"Nutrizionista non trovato"},400

        output_richiesta=nutrizionista_schema_for_dump.dump(nutrizionista),201
        session.close()
        return output_richiesta
