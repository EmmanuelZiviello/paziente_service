from datetime import datetime
from F_taste_paziente.db import get_session
from F_taste_paziente.repositories.richiesta_aggiunta_paziente_repository import RichiestaAggiuntaPazienteRepository
from F_taste_paziente.repositories.paziente_repository import PazienteRepository
from F_taste_paziente.repositories.nutrizionista_repository import NutrizionistaRepository
from F_taste_paziente.schemas.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteSchema

richiesta_schema_for_dump = RichiestaAggiuntaPazienteSchema()

class RichiestaAggiuntaPazienteService:

    @staticmethod
    def get_richieste_utente(paziente_id):
        session=get_session(role='patient')
        richieste=RichiestaAggiuntaPazienteRepository.find_new_requests(paziente_id, session)
        if richieste is None:
             session.close()
             return {"message":"Richieste non presenti nel database"},400
        output_richiesta=richiesta_schema_for_dump.dump(richieste,many=True),200
        session.close()
        return output_richiesta

    @staticmethod
    def gestisci_richiesta(id_paziente, id_nutrizionista, conferma):
            session=get_session(role='patient')
            richiesta = RichiestaAggiuntaPazienteRepository.find_by_id_paziente_and_id_nutrizionista(id_paziente, id_nutrizionista, session)

            if richiesta is None:
                session.close()
                return {'message': 'Richiesta non trovata'}, 204

            if conferma:
                if not richiesta.accettata:
                    if RichiestaAggiuntaPazienteRepository.find_active_request(id_paziente, session) is not None:
                        session.close()
                        return {'message': 'Non puoi accettare una richiesta senza revocare la precedente'}, 403
                    richiesta.accettata = True
                    richiesta.data_accettazione = datetime.now()
                    paziente = PazienteRepository.find_by_id(id_paziente, session)
                    if paziente is None:
                        session.close()
                        return {"message":"Paziente non trovato"},400
                    nutrizionista=NutrizionistaRepository.find_by_id(id_nutrizionista,session)
                    if nutrizionista is None:
                         session.close()
                         return {"message":"Nutrizionista non trovato"},400
                    richiesta.paziente = paziente
                    paziente=PazienteRepository.aggiorna_nutrizionista(id_paziente,id_nutrizionista,nutrizionista,session)
                    if paziente is None:
                         session.close()
                         return {"message":"Errore aggiornamento nutrizionista"},400
                    RichiestaAggiuntaPazienteRepository.save_richiesta(richiesta, session)
                    session.close()
                    return {"message": "Richiesta accettata con successo"}, 200
                session.close()
                return {'message': 'Richiesta già accettata'}, 403
            else:
                if not richiesta.accettata:
                    RichiestaAggiuntaPazienteRepository.delete_request(richiesta, session)
                    session.close()
                    return {"message": "Richiesta rifiutata con successo"}, 200
                session.close()
                return {'message': 'Non puoi rifiutare una richiesta già accettata'}, 403

    @staticmethod
    def revoca_condivisione(id_paziente):
            session=get_session(role='patient')
            paziente = PazienteRepository.find_by_id(id_paziente, session)
            if paziente is None:
                 session.close()
                 return {"message":"Paziente non trovato"},404
            richiesta = RichiestaAggiuntaPazienteRepository.find_active_request(id_paziente, session)
            if richiesta is None:
                session.close()
                return {'message': 'Richiesta non trovata'}, 404
            email_nutrizionista=''#la si deve ottenere da kafka dato che non fa parte del database attuale
            RichiestaAggiuntaPazienteRepository.create_richiesta_revocata(paziente, richiesta, email_nutrizionista,session)
            PazienteRepository.revoca_nutrizionista(paziente)
            RichiestaAggiuntaPazienteRepository.delete_request(richiesta, session)
            session.close()
            return {"message": "Richiesta revocata con successo"}, 204
