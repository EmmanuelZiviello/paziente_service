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

paziente_schema = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita'])
paziente_schema_for_load = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita', 'id_paziente'])
paziente_schema_for_dump = PazienteSchema(only=['id_paziente', 'sesso', 'data_nascita'])
paziente_schema_post_return = PazienteSchema(only=['id_paziente'])
pazienti_schema = PazienteSchema(many=True, only=['id_paziente'])

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
    def update_paziente_data(id_paziente, updated_data):
        session = get_session('patient')
        try:
            paziente=PazienteRepository.find_by_id(id_paziente,session)
            if paziente is None:
                return {"message":"Paziente non trovato"},404
            #lo fa ma si dovrebbe hashare la password nuova prima di aggiungerla al db
            #si invia la vecchia e nuova pw al servizio auth, la verifica e hasha la nuova se va bene
            paziente = PazienteRepository.update_by_id(paziente, updated_data, session)
            if  paziente is None:
                return {"message": "Dati paziente non aggiornati"}, 404
            return {"message": "Dati aggiornati con successo"}, 200
        except Exception as e:
            return {"message": f"Errore durante l'aggiornamento: {str(e)}"}, 500
        finally:
            session.close()

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
        if response.get("status_code") == "200":
         return {"message": "richiesta aggiunta a propria lista pazienti inviata con successo"}, 200   
        elif response.get("status_code") == "400":
            return {"esito add_richiesta":"Dati mancanti"}, 400
        elif response.get("status_code") == "403":
            return {"message": "richiesta già presente"}, 403
        
        #return {"message": "richiesta aggiunta a propria lista pazienti inviata con successo"}, 200


    #non credo vada bene perchè non controlla la password
    @staticmethod
    def delete_paziente(id_paziente):
        session = get_session('patient')
        try:
            if PazienteRepository.delete_by_id(id_paziente, session):
                return {"message": "Paziente eliminato con successo"}, 200
            return {"message": "Paziente non trovato"}, 404
        except Exception as e:
            return {"message": f"Errore durante l'eliminazione: {str(e)}"}, 500
        finally:
            session.close()
        

    @staticmethod
    def get_paziente_by_id(id_paziente):
        session = get_session('patient')
        # Recupero del paziente dal repository
        try:
            paziente=PazienteRepository.find_by_id(id_paziente,session)
            if not paziente:
                 return {"message":"Paziente non trovato"},400
            return paziente_schema_for_dump.dump(paziente), 200
        except Exception as e:
            # Log dell'errore per debugging
            print(f"Errore durante la ricerca del paziente: {e}")
            return None 
        finally:
            session.close()
    
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


