import os
from kafka import KafkaConsumer
import json
from F_taste_paziente.services.paziente_service import PazienteService
from F_taste_paziente.kafka.kafka_producer import send_kafka_message
# Percorso assoluto alla cartella dei certificati
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ottiene la cartella dove si trova questo script
CERTS_DIR = os.path.join(BASE_DIR, "..", "certs")  # Risale di un livello e accede alla cartella "certs"

# Configurazione Kafka su Aiven e sui topic
KAFKA_BROKER_URL = "kafka-ftaste-kafka-ftaste.j.aivencloud.com:11837"




consumer = KafkaConsumer(
    'patient.registration.request',
    'patient.login.request',
    'patient.cambiopw.request',
    'patient.recuperopw.request',
    'patient.delete.request',
    'patient.getAll.request',
    'patient.addDietitian.request',
    'patient.updateFk.request',
    'patient.removeFk.request',
    'patient.update.request',
    'patient.existGet.request',
    'dietitian.removeFk.request',
    'dietitian.getPazienti.request',
    'dietitian.getPaziente.request',
    'dietitian.registrationPatientFromDietitian.request',
    'patient.patch.request',
    bootstrap_servers=KAFKA_BROKER_URL,
    client_id="patient_consumer",
    group_id="patient_service",
    security_protocol="SSL",
    ssl_cafile=os.path.join(CERTS_DIR, "ca.pem"),  # Percorso del certificato CA
    ssl_certfile=os.path.join(CERTS_DIR, "service.cert"),  # Percorso del certificato client
    ssl_keyfile=os.path.join(CERTS_DIR, "service.key"),  # Percorso della chiave privata
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

def consume(app):
    #Ascolta Kafka e chiama il Service per la registrazione
    with app.app_context():
        for message in consumer:
            data = message.value
            topic=message.topic
            if topic ==  "patient.registration.request":
                response, status = PazienteService.register_paziente(data)  # Chiama il Service
                topic_producer = "patient.registration.success" if status == 201 else "patient.registration.failed"
                send_kafka_message(topic_producer, response)
            
            elif topic == "patient.login.request":
                response,status=PazienteService.login_paziente(data)
                topic_producer="patient.login.success" if status == 200 else "patient.login.failed"
                send_kafka_message(topic_producer,response)
            
            elif topic == "patient.cambiopw.request":
                response,status=PazienteService.cambio_pw(data)
                topic_producer="patient.cambiopw.success" if status == 200 else "patient.cambiopw.failed"
                send_kafka_message(topic_producer,response)
            
            elif topic == "patient.recuperopw.request":
                response,status=PazienteService.recupero_pw(data)
                topic_producer="patient.recuperopw.success" if status == 200 else "patient.recuperopw.failed"
                send_kafka_message(topic_producer,response)

            elif topic == "patient.delete.request":
                response,status=PazienteService.delete(data)
                topic_producer="patient.delete.success" if status == 200 else "patient.delete.failed"
                send_kafka_message(topic_producer,response)
            
            elif topic == "patient.getAll.request":
                response,status=PazienteService.getAll()
                topic_producer="patient.getAll.success" if status == 200 else "patient.getAll.failed"
                send_kafka_message(topic_producer,response)
            
            elif topic == "patient.addDietitian.request":
                response,status=PazienteService.add_dietitian(data)
                topic_producer="patient.addDietitian.success" if status == 200 else "patient.addDietitian.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "patient.updateFk.request":
                response,status=PazienteService.update_dietitian(data)
                topic_producer="patient.updateFk.success" if status == 200 else "patient.updateFk.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "patient.removeFk.request":
                response,status=PazienteService.remove_dietitian(data)
                topic_producer="patient.removeFk.success" if status == 200 else "patient.removeFk.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "dietitian.getPazienti.request":
                response,status=PazienteService.get_pazienti(data)
                topic_producer="dietitian.getPazienti.success" if status == 200 else "dietitian.getPazienti.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "dietitian.removeFk.request":
                response,status=PazienteService.remove_paziente(data)
                topic_producer="dietitian.removeFk.success" if status == 200 else "dietitian.removeFk.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "dietitian.getPaziente.request":
                response,status=PazienteService.get_paziente(data)
                topic_producer="dietitian.getPaziente.success" if status == 200 else "dietitian.getPaziente.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "patient.update.request":
                response,status=PazienteService.update_paziente(data)
                topic_producer="patient.update.success" if status == 200 else "patient.update.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "patient.existGet.request":
                response,status=PazienteService.exist_and_get(data)
                topic_producer="patient.existGet.success" if status == 200 else "patient.existGet.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "dietitian.registrationPatientFromDietitian.request":
                response,status=PazienteService.nutrizionista_register_paziente(data)
                topic_producer="dietitian.registrationPatientFromDietitian.success" if status == 201 else "dietitian.registrationPatientFromDietitian.failed"
                send_kafka_message(topic_producer,response)
            elif topic == "patient.patch.request":
                response,status=PazienteService.patch(data)
                topic_producer="patient.patch.success" if status == 200 else "patient.patch.failed"
                send_kafka_message(topic_producer,response)


            