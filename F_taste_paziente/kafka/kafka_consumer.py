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
PATIENT_REGISTRATION_REQUEST_TOPIC = "patient.registration.request"
PATIENT_REGISTRATION_SUCCESS_TOPIC = "patient.registration.success"
PATIENT_REGISTRATION_FAILED_TOPIC = "patient.registration.failed"



consumer = KafkaConsumer(
    'patient.registration.request',
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

def consume():
    #Ascolta Kafka e chiama il Service per la registrazione
    for message in consumer:
        s_paziente = message.value
        response, status = PazienteService.register_paziente(s_paziente)  # Chiama il Service
        
        topic = "patient.registration.success" if status == 201 else "patient.registration.failed"
        send_kafka_message(topic, response)
