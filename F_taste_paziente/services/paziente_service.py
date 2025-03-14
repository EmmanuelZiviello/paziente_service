from datetime import datetime
from F_taste_paziente.repositories.paziente_repository import PazienteRepository
#from flaskr.utils.kafka import KafkaProducer
from F_taste_paziente.db import get_session
from F_taste_paziente.schemas.paziente import PazienteSchema
from F_taste_paziente.repositories.informativa_repository import InformativaRepository
from F_taste_paziente.utils.id_generation import genera_id_valido
from F_taste_paziente.utils.hashing_password import hash_pwd,check_pwd
from F_taste_paziente.utils.jwt_token_factory import JWTTokenFactory
import F_taste_paziente.utils.credentials as credentials
from F_taste_paziente.utils.jwt_functions import ACCESS_EXPIRES
from flask_jwt_extended import create_access_token
from F_taste_paziente.utils.encrypting_id import encrypt_id
from F_taste_paziente.kafka.kafka_producer import send_kafka_message
from F_taste_paziente.utils.kafka_helpers import wait_for_kafka_response
from F_taste_paziente.utils.password_generator import PasswordGenerator as pg


paziente_schema = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita'])
paziente_schema_for_load = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita', 'id_paziente'])
paziente_schema_for_dump = PazienteSchema(only=['id_paziente', 'sesso', 'data_nascita'])
paziente_schema_post_return = PazienteSchema(only=['id_paziente'])
pazienti_schema = PazienteSchema(many=True, only=['id_paziente'])
paziente_schema_put = PazienteSchema(exclude=['email','password'], partial=['id_nutrizionista'])

jwt_factory = JWTTokenFactory()

class PazienteService:

    
    @staticmethod
    def login_paziente(s_paziente):
        if "email" not in s_paziente or "password" not in s_paziente:
            return {"esito_login": "Dati mancanti"}, 400
        session=get_session('patient')
        email_paziente = s_paziente["email"]
        password = s_paziente["password"]
        paziente=PazienteRepository.find_by_email(email_paziente,session)
        if paziente is None:
            session.close()
            return {"esito_login": "Paziente non trovato"}, 401
        if check_pwd(password, paziente.password):
            session.close()
            return {
                "esito_login": "successo",
                "access_token": jwt_factory.create_access_token(paziente.id_paziente, 'patient'),
                "refresh_token": jwt_factory.create_refresh_token(paziente.id_paziente, 'patient'),
                "id_paziente": paziente.id_paziente
            }, 200

        session.close()
        return {"esito_login": "password errata"}, 401

    @staticmethod
    def register_paziente(s_paziente):
        session = get_session('patient')

        # Validazione dati in ingresso
        validation_errors = paziente_schema.validate(s_paziente)
        if validation_errors:
            session.close()
            return validation_errors, 400

        # Verifica se l'email esiste già
        if PazienteRepository.find_by_email(s_paziente['email'], session) is not None:
            session.close()
            return {"esito_registrazione": "email già utilizzata"}, 409

        # Genera un ID valido per il paziente
        s_paziente['id_paziente'] = genera_id_valido()

        # Crea l'oggetto Paziente e salva la password in formato hash
        paziente = paziente_schema_for_load.load(s_paziente, session=session)
        paziente.password = hash_pwd(s_paziente['password'])

        # Salva il paziente nel database
        PazienteRepository.add(paziente, session)

        # Prepara la risposta con i dati del paziente
        output_richiesta = paziente_schema_post_return.dump(paziente), 201
        session.close()
        
        return output_richiesta
    
    @staticmethod
    def cambio_pw(s_paziente):
        if "password" not in s_paziente or "new_password" not in s_paziente or "id_paziente" not in s_paziente:
            return {"esito_cambiopw": "Dati mancanti"}, 400
        session = get_session('patient')
        password=s_paziente["password"]
        new_password=s_paziente["new_password"]
        id_paziente=s_paziente["id_paziente"]
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"esito_cambiopw": "Paziente non trovato"}, 401
        if check_pwd(password,paziente.password):
            paziente.password=hash_pwd(new_password)
            PazienteRepository.add(paziente,session)
            session.close()
            return {"message":"Password aggiornata con successo"}, 200
        else:
            session.close()
            return {"message":"Vecchia password errata"}, 400

    @staticmethod
    def recupero_pw(s_paziente):
        if "id_paziente" not in s_paziente:
            return {"esito recuperopw":"Dati mancanti"}, 400
        session=get_session('patient')
        id_paziente=s_paziente["id_paziente"]
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"esito_cambiopw": "Paziente non trovato"}, 401
        session.close()
        token=create_access_token(credentials.reset_password,ACCESS_EXPIRES)
        link=credentials.endpoint + "/password_reset?jwt=" + token + "&id=" + encrypt_id(id_paziente)
        # **Invia un messaggio Kafka al servizio Email**
        '''
        email_message = {
            "email": paziente.email,
            "subject": "Recupero Password",
            "body": f"Clicca sul link per reimpostare la password: {link}"
        }
        send_kafka_message("email.send.request", email_message)
        '''
        return {"esito_cambiopw":"Email di recupero password inviata con successo"}, 200


    @staticmethod
    def update_paziente_data(id_paziente, s_paziente):
        session = get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message":"Paziente non trovato"}, 404
            #lo fa ma si dovrebbe hashare la password nuova prima di aggiungerla al db
            #si invia la vecchia e nuova pw al servizio auth, la verifica e hasha la nuova se va bene
        if "sesso" in s_paziente and "data_nascita" not in s_paziente or "sesso" not in s_paziente and "data_nascita" in s_paziente:
            return {"message" : "Missing sesso or data_nascita field."}, 400
        # Cambio password e dati sensibili
        sensible_data=False
        if "sesso" in s_paziente and "data_nascita" in s_paziente:
            sesso=s_paziente["sesso"]
            data_nascita=s_paziente["data_nascita"]
            new_date=datetime.strptime(data_nascita, '%Y-%m-%d').date()
            paziente.sesso=sesso
            paziente.data_nascita=new_date
            sensible_data=True
        #Cambio della password
                # Gestione dell'errore se mancano i campi della password
        if "new_password" not in s_paziente or "password" not in s_paziente:
            session.close()
            return {"message" : "Bad Request"}, 400
        password=s_paziente["password"]
        new_password=s_paziente["new_password"]
        if not pg.isAStrongPassword(new_password):
            session.close()
            return {"message" : "La nuova password inserita non è abbastanza sicura."}, 400
        if not check_pwd(password, paziente.password):
            session.close()
            return {"message": "vecchia password errata"}, 401
        paziente.password = hash_pwd(new_password)
        PazienteRepository.add(paziente)
        session.close()
        if sensible_data:
            return {"message" : "Cambi password e dati sensibili avvenuti con successo."}, 201
        else:
            return { 'message' : 'cambio password avvenuto con successo'}, 201
        






    @staticmethod
    def delete(s_paziente):
        if "id_paziente" not in s_paziente:
            return {"esito delete":"Dati mancanti"}, 400
        session=get_session('admin')
        id_paziente=s_paziente["id_paziente"]
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"esito delete": "Paziente non trovato"}, 404
        PazienteRepository.delete(paziente,session)
        session.close()
        return {"message":"Paziente eliminato con successo"}, 200
    
    @staticmethod
    def getAll():
        session=get_session('admin')
        pazienti_data=PazienteRepository.get_all_pazienti(session)
        output_richiesta={"pazienti": pazienti_schema.dump(pazienti_data)}, 200
        session.close()
        return output_richiesta
    
    @staticmethod
    def get_pazienti(s_paziente):
        if "id_nutrizionista" not in s_paziente:
            return {"esito get_pazienti":"Dati mancanti"},400
        session=get_session('patient')
        id_nutrizionista=s_paziente["id_nutrizionista"]
        pazienti_data=PazienteRepository.get_pazienti_from_id_nutrizionista(id_nutrizionista,session)
        output_richiesta={"pazienti": pazienti_schema.dump(pazienti_data)}, 200
        session.close()
        return output_richiesta

    @staticmethod
    def add_dietitian(s_paziente):
        if "id_paziente" not in s_paziente or "id_nutrizionista" not in s_paziente:
            return {"esito add_Dietitian":"Dati mancanti"}, 400
        id_paziente=s_paziente["id_paziente"]
        id_nutrizionista=s_paziente["id_nutrizionista"]
        session=get_session('dietitian')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        # Controlliamo se il paziente è già seguito
        if paziente.id_nutrizionista is not None:
            if paziente.id_nutrizionista == id_nutrizionista:
                session.close()
                return {"message": "segui già questo paziente"}, 304
            else:
                session.close()
                return {"message": "Paziente seguito da un altro nutrizionista"}, 403
        
        session.close()
        message={"id_paziente":id_paziente,"id_nutrizionista":id_nutrizionista}
        send_kafka_message("richieste.add.request",message)
        response = wait_for_kafka_response(["richieste.add.success", "richieste.add.failed"])

        if response is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500

        if response.get("status_code") == "200":
         return {"message": "richiesta aggiunta a propria lista pazienti inviata con successo"}, 200   
        elif response.get("status_code") == "400":
            return {"esito add_richiesta":"Dati mancanti"}, 400
        elif response.get("status_code") == "403":
            return {"message": "richiesta già presente"}, 403
        
        #return {"message": "richiesta aggiunta a propria lista pazienti inviata con successo"}, 200

    @staticmethod
    def update_dietitian(s_paziente):
        if "id_paziente" not in s_paziente or "id_nutrizionista" not in s_paziente:
                return {"status_code":"400"}, 400
                #return {"esito update_Dietitian":"Dati mancanti"}, 400
        id_paziente=s_paziente["id_paziente"]
        id_nutrizionista=s_paziente["id_nutrizionista"]
        session=get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"status_code":"404"}, 404
            #return {"message": "Paziente non presente nel database"}, 404

        #controlla che quel nutrizionista esista veramente
        message={"id_nutrizionista":id_nutrizionista}
        send_kafka_message("dietitian.exist.request",message)
        response = wait_for_kafka_response(["dietitian.exist.success", "dietitian.exist.failed"])
        #controllo sul valore in response per capire se si può aggiornare il db
        if response is None:
            session.close()
            return {"status_code":"500"}, 500
            #return {"message": "Errore nella comunicazione con Kafka"}, 500
        if response.get("status_code") == "200":
            PazienteRepository.update_nutrizionista(paziente,id_nutrizionista,session)
            session.close()
            return {"status_code":"200"}, 200
            #return {"message": "nutrizionista aggiornato con successo"}, 200
        elif response.get("status_code") == "400":
            return {"status_code":"400"}, 400
        elif response.get("status_code") == "404":
            return {"status_code":"404"}, 404
        

    @staticmethod
    def remove_dietitian(s_paziente):
        if "id_paziente" not in s_paziente:
                return {"status_code":"400"}, 400
                #return {"esito remove_Dietitian":"Dati mancanti"}, 400
        id_paziente=s_paziente["id_paziente"]
        session=get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"status_code":"404"}, 404
            #return {"message": "Paziente non presente nel database"}, 404
        id_nutrizionista=paziente.id_nutrizionista
        if id_nutrizionista is None:
            session.close()
            return {"status_code":"200"}, 200
        #riceve l'email del nutrizionista salvato nel paziente
        message={"id_nutrizionista":id_nutrizionista}
        send_kafka_message("dietitian.email.request",message)
        response = wait_for_kafka_response(["dietitian.email.success", "dietitian.email.failed"])
        #controllo sul valore in response per capire se si può aggiornare il db
        if response is None:
            session.close()
            return {"status_code":"500"}, 500
            #return {"message": "Errore nella comunicazione con Kafka"}, 500
        if response.get("status_code") == "200":
            #aggiungere controllo sull'email_nutrizionista in response
            email_nutrizionista = response.get("email_nutrizionista")
            if email_nutrizionista:
                PazienteRepository.update_nutrizionista(paziente,None,session)
                session.close()
                return {"status_code": "200", "email_nutrizionista": email_nutrizionista}, 200
                #return {"message": "nutrizionista rimosso dal paziente con successo"}, 200
            session.close()
            return {"status_code":"400"}, 400
        elif response.get("status_code") == "400":
            session.close()
            return {"status_code":"400"}, 400
        elif response.get("status_code") == "404":
            session.close()
            return {"status_code":"404"}, 404
    
    @staticmethod
    def remove_paziente(s_paziente):
        if "id_paziente" not in s_paziente or "id_nutrizionista" not in s_paziente:
            return {"esito remove_paziente":"Dati mancanti"}, 400
        session=get_session('patient')
        id_paziente=s_paziente["id_paziente"]
        id_nutrizionista=s_paziente["id_nutrizionista"]
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        if (paziente.id_nutrizionista != id_nutrizionista):
            session.close()
            return {"message": "non segui questo paziente"}, 403
        PazienteRepository.update_nutrizionista(paziente,None,session)
        session.close()
        return {"message": "non segui più questo paziente"}, 200
    

    @staticmethod
    def get_paziente(s_paziente):
        if "id_paziente" not in s_paziente or "id_nutrizionista" not in s_paziente:
            return {"esito remove_paziente":"Dati mancanti"}, 400
        session=get_session('patient')
        id_paziente=s_paziente["id_paziente"]
        id_nutrizionista=s_paziente["id_nutrizionista"]
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        if (paziente.id_nutrizionista != id_nutrizionista):
            session.close()
            return {"message" : "paziente seguito da un altro nutrizionista"}, 403
        #prima di questo codice ci vuole un collegamento kafka con misurazioni per aggiornare ai valori più recenti
        #anche se non l ho inserito perchè nel model originale non vengono salvati i parametri della misurazione
        #quindi lascio i valori come il peso e l'altezza nel servizio misurazioni per maggior separazione di dati tra servizi
        pazienteSchema = PazienteSchema(only=['id_paziente', 'sesso', 'data_nascita'])
        paziente_dump = pazienteSchema.dump(paziente)
        session.close()
        return paziente_dump, 200
    

    @staticmethod
    def update_paziente(s_paziente):
        if "id_paziente" not in s_paziente or "id_nutrizionista" not in s_paziente or ("sesso" not in s_paziente and "data_nascita" not in s_paziente):
            return {"esito update_paziente":"Dati mancanti"}, 400
        id_paziente=s_paziente["id_paziente"]
        id_nutrizionista=s_paziente["id_nutrizionista"]
        session=get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        if paziente.id_nutrizionista is None:
            session.close()
            return {'message' : 'Paziente non seguito da un nutrizionista'}, 403
        #Se il paziente è associato al medico che fa la richiesta vengono gestiti i casi dinamicamente
        if paziente.id_nutrizionista == id_nutrizionista:
            if "data_nascita" in s_paziente:
                paziente.data_nascita=datetime.strptime(s_paziente["data_nascita"], '%Y-%m-%d').date()
            if "sesso" in s_paziente:
                paziente.sesso=s_paziente["sesso"]
            PazienteRepository.add(paziente,session)#per aggiornare i valori nel db
            output_richiesta=paziente_schema_put.dump(paziente), 200
            session.close()
            return output_richiesta
        else:
            session.close()
            return {'message' : 'paziente seguito da un\'altro nutrizionista'}, 403
            

        



        

    
    @staticmethod
    def delete_paziente(id_paziente,password):
        session = get_session('patient')
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message": "Paziente non presente nel database"}, 404
        
        if check_pwd(password,paziente.password):
            PazienteRepository.delete(paziente,session)
            session.close()
            return {'message': 'Paziente eliminato con successo'}, 200
        session.close()
        return {'message': 'Errore credenziali'}, 403

        

    @staticmethod
    def get_paziente_by_id(id_paziente):
        session = get_session('patient')
        # Recupero del paziente dal repository
        paziente=PazienteRepository.find_by_id(id_paziente,session)
        if paziente is None:
            session.close()
            return {"message":"Paziente non trovato"},400
        session.close()
        paziente_output=paziente_schema_for_dump.dump(paziente)
        if paziente.sesso is None and paziente.data_nascita is None:
            return {"id_paziente":paziente_output.id_paziente}, 206
        return paziente_output, 200

    
    @staticmethod
    def visualizza_informativa():
        session=get_session('patient')
        informativa=InformativaRepository.get_last_privacy_policy_by_type("paziente",session)
        if informativa is None:
            session.close()
            return {"message":""},204
        session.close()
        return {
            'informativa':informativa.testo_informativa,
            'link_informativa':informativa.link_inf_estesa
        },200


