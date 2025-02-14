from F_taste_paziente.models.consensi_utente import ConsensiUtenteModel
from F_taste_paziente.models.log_consensi import LOGConsensi
from F_taste_paziente.db import get_session
from sqlalchemy.exc import SQLAlchemyError

class ConsensiUtenteRepository:

    @staticmethod
    def find_consensi_by_paziente_id(paziente_id, session=None):
        session = session or get_session('patient')
        return ConsensiUtenteModel.find_consensi_of_paziente(paziente_id, session)


    @staticmethod
    def save_consensi(consensi_utente, session=None):
        session = session or get_session('patient')
        session.add(consensi_utente)
        session.commit()

    @staticmethod
    def add_log_consensi(tipologia, valore, id_paziente, session=None):
        session = session or get_session('patient')
        log_consensi = LOGConsensi(tipologia, id_paziente=id_paziente, valore=valore)
        if log_consensi:
            session.add(log_consensi)


    @staticmethod
    def update_consensi(consensi_paziente, updated_data, session=None):
        session = session or get_session('patient')
        try:
            if consensi_paziente:
                for key, value in updated_data.items():
                    setattr(consensi_paziente, key, value)
                session.commit()
                return consensi_paziente
            return None
        except SQLAlchemyError:
            session.rollback()
            return None  
        finally:
            session.close()