from datetime import datetime
from flaskr.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP

class RichiestaRevocataModel(Base):
    __tablename__ = "richiesta_revocata"

    id_richiesta = Column(Integer, primary_key=True)
    data_richiesta = Column(TIMESTAMP, nullable = False)
    data_accettazione = Column(TIMESTAMP, nullable = True)
    data_revoca = Column(TIMESTAMP, nullable = True)
    email_nutrizionista = Column(String(45),  
                            nullable=False)
    fk_paziente = Column(String(7), 
                            ForeignKey("paziente.id_paziente"), 
                            nullable=False)
    

    def __init__(self, fk_paziente, email_nutrizionista, data_richiesta, data_accettazione):
        self.fk_paziente = fk_paziente
        self.email_nutrizionista = email_nutrizionista
        self.data_richiesta = data_richiesta
        self.data_accettazione = data_accettazione
        self.data_revoca = datetime.now()

    def __repr__(self):
        return 'RichiestaAggiuntaPazienteModel(fk_paziente=%r, fk_nutrizionista=%r, data_richiesta=%r, data_accettazione=%r, data_revoca=%r)' % (self.fk_paziente, self.fk_nutrizionista, self.data_richiesta, self.data_accettazione, self.data_revoca)
    
    def __json__(self):
        return { 'fk_paziente': self.fk_paziente, 
                'fk_nutrizionista': self.fk_nutrizionista, 
                'data_richiesta': self.data_richiesta,
                'data_accettazione': self.data_accettazione,
                'data_revoca': self.data_revoca }
    
  
    @classmethod
    def find_by_id_paziente_and_id_nutrizionista(cls, id_paziente, id_nutrizionista, session) -> "RichiestaRevocataModel":
        result = session.query(cls).filter_by(fk_paziente = id_paziente, 
                                              fk_nutrizionista = id_nutrizionista).first()
        return result
    
    @classmethod
    def find_by_id_paziente(cls, id_paziente, session) -> "RichiestaRevocataModel":
        result = session.query(cls).filter_by(fk_paziente = id_paziente).all()
        return result