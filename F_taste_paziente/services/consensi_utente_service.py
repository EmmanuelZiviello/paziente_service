from F_taste_paziente.db import get_session
from F_taste_paziente.repositories.consensi_utente_repository import ConsensiUtenteRepository
from F_taste_paziente.repositories.paziente_repository import PazienteRepository
from F_taste_paziente.schemas.consensi_utente import ConsensiUtenteSchema

possible_requests = (
    "storage_from_Google_fit",
    "storage_from_Health_kit",
    "condivisione_misurazioni_paziente",
    "management_user_consent",
    "statistic_user_consent",
    "trainingAI_user_consent"
)

consensi_schema_for_dump=ConsensiUtenteSchema(exclude=['fk_paziente'])

class ConsensiUtenteService:

    @staticmethod
    def get_consensi_utente(paziente_id):
        session = get_session(role='patient')
        consensi_utente = ConsensiUtenteRepository.find_consensi_by_paziente_id(paziente_id, session)
        if not consensi_utente:
            return {"message":"Consensi non presenti nel database"},400
        output_richiesta=consensi_schema_for_dump.dump(consensi_utente),200
        session.close()
        return output_richiesta

    @staticmethod
    def update_consensi_utente(paziente_id, json_data):
        # Validazione dei dati
        for key in json_data:
            if key not in possible_requests:
                return {"message": f"Il consenso \"{key}\" non è un consenso valido."}, 400
        
        session = get_session(role='patient')
        paziente = PazienteRepository.find_by_id(paziente_id, session)
        if paziente is None:
            session.close()
            return {'message': 'Paziente non presente nel db'}, 404
        
        consensi_utente = ConsensiUtenteRepository.find_consensi_by_paziente_id(paziente_id, session)
        if consensi_utente is None:
            session.close()
            return {'message': 'Consensi utente non presenti nel db'}, 404
        
        consensi_utente=ConsensiUtenteRepository.update_consensi(consensi_utente,json_data,session)
        # Aggiornamento dei consensi creando dei log consensi
        for key in possible_requests:
            if key in json_data:
                ConsensiUtenteRepository.add_log_consensi(key, json_data[key], paziente_id, session)
        
        session.close()
        return {"message": "Consensi utente modificati con successo"}, 201
