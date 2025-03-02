from F_taste_paziente.models.informativa import InformativaBreveModel
from F_taste_paziente.db import get_session
from sqlalchemy.exc import SQLAlchemyError

class InformativaRepository:

    @staticmethod
    def get_last_privacy_policy_by_type(tipologia, session=None):
        session = session or get_session('patient')
        return session.query(InformativaBreveModel).filter_by(tipologia_informativa=tipologia).order_by(InformativaBreveModel.data_inserimento.desc()).first()



  

   


  