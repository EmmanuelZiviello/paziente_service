from F_taste_paziente.repositories.paziente_repository import PazienteRepository
from F_taste_paziente.models.paziente import PazienteModel
from F_taste_paziente.db import get_session
from F_taste_paziente.kafka.kafka_producer import send_kafka_message
from F_taste_paziente.utils.kafka_helpers import wait_for_kafka_response






class NutrizionistaService:


    @staticmethod
    def get_nutrizionista_by_paziente(id_paziente):
        session=get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        if paziente.id_nutrizionista is None:
            session.close()
            return {'message' : 'Paziente non seguito da un nutrizionista'}, 403
        id_nutrizionista=paziente.id_nutrizionista
        session.close()
        message={"id_nutrizionista":id_nutrizionista}
        send_kafka_message("patient.getNutrizionista.request",message)
        response=wait_for_kafka_response(["patient.getNutrizionista.success", "patient.getNutrizionista.failed"])
        return response
        
    