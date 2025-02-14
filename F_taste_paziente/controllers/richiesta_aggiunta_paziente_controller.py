from flask import request
from flask_restx import Resource,fields
from flask_jwt_extended import get_jwt_identity
from F_taste_paziente.utils.jwt_custom_decorators import paziente_required
from F_taste_paziente.schemas.richiesta_aggiunta_paziente import RichiestaAggiuntaPazienteSchema
from F_taste_paziente.services.richiesta_aggiunta_paziente_service import RichiestaAggiuntaPazienteService
from F_taste_paziente.namespaces import paziente_ns

gestisciRichiestaRequestModel = paziente_ns.model('gestisci Richiesta Request Model', {
    'fk_nutrizionista' : fields.Integer(required=True),
    'conferma' : fields.Boolean(required=True),
}, strict=True)

deleteRichiestaRequestModel = paziente_ns.model('delete Richiesta Request Model', {
    'fk_nutrizionista' : fields.String(required=True),
}, strict=True)

richiesta_schema_for_dump = RichiestaAggiuntaPazienteSchema()

class RichiestaAggiuntaPaziente(Resource):

    @paziente_ns.doc('recupera le richieste attive')
    @paziente_required()
    def get(self):
        identity = get_jwt_identity()
        return RichiestaAggiuntaPazienteService.get_richieste_utente(identity)

    @paziente_ns.expect(gestisciRichiestaRequestModel)
    @paziente_ns.doc('accetta/revoca la richiesta di aggiunta')
    @paziente_required()
    def put(self):
        identity = get_jwt_identity()
        json = request.get_json()
        if not json:
            return {"message": "Dati non forniti"}, 400
        return RichiestaAggiuntaPazienteService.gestisci_richiesta(identity, json['fk_nutrizionista'], json['conferma'])

    @paziente_required()
    @paziente_ns.doc('elimina la condivisione con il tuo nutrizionista')
    def delete(self):
        identity = get_jwt_identity()
        return RichiestaAggiuntaPazienteService.revoca_condivisione(identity)
