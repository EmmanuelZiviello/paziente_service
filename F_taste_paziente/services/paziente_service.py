from F_taste_paziente.repositories.paziente_repository import PazienteRepository
#from flaskr.utils.kafka import KafkaProducer
from F_taste_paziente.db import get_session

class PazienteService:

  

    @staticmethod
    def update_paziente_data(id_paziente, updated_data):
        session = get_session('patient')
        try:
            paziente=PazienteRepository.find_by_id(id_paziente,session)
            if paziente is None:
                return {"message":"Paziente non trovato"},404
            paziente = PazienteRepository.update_by_id(paziente, updated_data, session)
            if  paziente is None:
                return {"message": "Dati paziente non aggiornati"}, 404
            return {"message": "Dati aggiornati con successo"}, 200
        except Exception as e:
            return {"message": f"Errore durante l'aggiornamento: {str(e)}"}, 500
        finally:
            session.close()

    @staticmethod
    def delete_paziente(id_paziente):
        session = get_session('patient')
        try:
            if PazienteRepository.delete_by_id(id_paziente, session):
                return {"message": "Paziente eliminato con successo"}, 200
            return {"message": "Paziente non trovato"}, 404
        except Exception as e:
            return {"message": f"Errore durante l'eliminazione: {str(e)}"}, 500
        finally:
            session.close()
        

    @staticmethod
    def get_paziente_by_id(id_paziente):
        session = get_session('patient')
        # Recupero del paziente dal repository
        try:
            paziente=PazienteRepository.find_by_id(id_paziente,session)
            if not paziente:
                 return None
            return paziente
        except Exception as e:
            # Log dell'errore per debugging
            print(f"Errore durante la ricerca del paziente: {e}")
            return None 
        finally:
            session.close()
