from F_taste_paziente.db import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from datetime import datetime

# Questa classe rappresenta la tabella contenente tutti i log riguardo all'accettazione dei consensi da parte degli utenti

class LOGConsensi(Base):
    
    __tablename__ = "consensi_utente_log"

    id = Column(Integer, primary_key=True)
    tipologia = Column(String(500), nullable=False)
    id_paziente = Column(String(7), default=False, nullable=False)
    valore = Column(Boolean, nullable=False)
    data_modifica = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return " tipologia: {0}, id_paziente :{1}, valore :{2}, data_modifica:{3}".format(self.tipologia, self.id_paziente, self.valore, self.data_modifica)

    def __init__(self, tipologia, id_paziente, valore):
        self.tipologia = tipologia
        self.id_paziente = id_paziente
        self.valore = valore
        self.data_modifica = datetime.now()

    def __repr__(self):
        return 'LOGConsensi(id=%s, tipologia=%s, id_paziente=%s, valore=%s, data_modifica=%s)' % (self.id, self.tipologia, self.id_paziente, self.valore, self.data_modifica)

    def __json__(self):
        return { 'id': self.id, 'tipologia': self.tipologia, 'id_paziente': self.id_paziente, 'valore': self.valore, 'data_modifica': self.data_modifica }
    
    @classmethod
    def get_log_consensi(cls, session):
        return session.query(cls).all()
    