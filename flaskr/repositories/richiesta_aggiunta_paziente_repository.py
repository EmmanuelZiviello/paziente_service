from flaskr.models.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteModel
from flaskr.models.paziente import PazienteModel
from flaskr.models.nutrizionista import NutrizionistaModel
from flaskr.models.richiesta_revocata import RichiestaRevocataModel
from datetime import datetime
from flaskr.db import get_session

class RichiestaAggiuntaPazienteRepository:

    @staticmethod
    def find_new_requests(paziente_id, session=None):
        session = session or get_session('patient')
        return RichiestaAggiuntaPazienteModel.query.filter_by(paziente_id=paziente_id, accettata=False).all()

    @staticmethod
    def find_by_id_paziente_and_id_nutrizionista(paziente_id, nutrizionista_id, session=None):
        session = session or get_session('patient')
        return RichiestaAggiuntaPazienteModel.query.filter_by(paziente_id=paziente_id, nutrizionista_id=nutrizionista_id).first()

    @staticmethod
    def find_active_request(paziente_id, session=None):
        session = session or get_session('patient')
        return RichiestaAggiuntaPazienteModel.query.filter_by(paziente_id=paziente_id, accettata=True).first()

    @staticmethod
    def delete_request(richiesta, session=None):
        session = session or get_session('patient')
        session.delete(richiesta)
        session.commit()

    @staticmethod
    def save_richiesta(richiesta, session=None):
        session = session or get_session('patient')
        session.add(richiesta)
        session.commit()

    @staticmethod
    def create_richiesta_revocata(paziente, richiesta, email_nutrizionista,session=None):
        session = session or get_session('patient')
        richiesta_revocata = RichiestaRevocataModel(paziente.id_paziente, email_nutrizionista, richiesta.data_richiesta, richiesta.data_accettazione)
        session.add(richiesta_revocata)
        session.commit()
