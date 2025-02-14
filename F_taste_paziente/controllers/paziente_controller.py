from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource,fields
from F_taste_paziente.services.paziente_service import PazienteService
from F_taste_paziente.namespaces import paziente_ns
from F_taste_paziente.utils.jwt_custom_decorators import paziente_required
from F_taste_paziente.db import get_session
from F_taste_paziente.schemas.paziente import PazienteSchema

#json model required by flask_restx for expectations


update_patient_data = paziente_ns.model('cambio password',{
    'sesso': fields.Boolean('sex of the patient', required=False),
    'data_nascita': fields.String('date of birth', required=False),
    'password': fields.String('password of the paziente', required = True),
    'new_password' : fields.String('new password', required = True)
}, strict = True)

get_paziente_model = paziente_ns.model('get_paziente_secret_model', {
    'id_paziente' : fields.String('id of paziente')
}, strict = True)


paziente_model_for_delete = paziente_ns.model('paziente_model_for_delete', {
    'password': fields.String('password of the paziente')
}, strict = True)


######da levare, solo per registrare nel db i pazienti
signup_paziente = paziente_ns.model('singup_paziente', {
    'password': fields.String('password of the paziente'),
    'email': fields.String('mail of the paziente'),
    'data_nascita': fields.String("format yyyy-MM-dd"),
    'sesso': fields.Boolean('true = maschio , false=femmina')
}, strict=True)

paziente_schema = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita'])
paziente_schema_post_return = PazienteSchema(only=['id_paziente'])
paziente_schema_put = PazienteSchema(only=['id_paziente','password'])
paziente_schema_delete = PazienteSchema(only=[ 'password'])
paziente_schema_for_dump = PazienteSchema(only=['id_paziente', 'sesso', 'data_nascita'])
paziente_schema_for_load = PazienteSchema(only = ['email', 'password', 'sesso', 'data_nascita', 'id_paziente'])
check_put_schema = PazienteSchema(only=['id_paziente','password'])


class Paziente(Resource):

   

    @paziente_required()
    @paziente_ns.expect(update_patient_data)
    @paziente_ns.doc('Cambio password, sesso e data di nascita del paziente.')
    def put(self):
        updated_data = request.get_json()
        if not updated_data:
            return {"message": "Dati non forniti"}, 400
        id_paziente = get_jwt_identity()
        return PazienteService.update_paziente_data(id_paziente, updated_data)

    @paziente_required()
    @paziente_ns.doc('recupera paziente')
    def get(self):
        id_paziente = get_jwt_identity()
        return PazienteService.get_paziente_by_id(id_paziente)

    @paziente_required()
    @paziente_ns.expect(paziente_model_for_delete)
    @paziente_ns.doc('elimina paziente')
    def delete(self):
        paziente_json = request.get_json()
        if not paziente_json or 'password' not in paziente_json:
            return {"message": "Password richiesta"}, 400
        id_paziente = get_jwt_identity()
        return PazienteService.delete_paziente(id_paziente, paziente_json['password'])
    
    ###########da levare, è solo per registrare su questo db i pazienti
    @paziente_ns.expect(signup_paziente)
    @paziente_ns.doc('signup paziente')
    def post(self):
        s_paziente = request.get_json()        
        # Chiamata al servizio di registrazione del paziente
        return PazienteService.register_paziente(s_paziente)

