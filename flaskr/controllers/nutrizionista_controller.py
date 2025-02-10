from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource,fields
from flaskr.services.nutrizionista_service import NutrizionistaService
from flaskr.namespaces import paziente_ns
from flaskr.utils.jwt_custom_decorators import paziente_required
from flaskr.db import get_session
from flaskr.schemas import nutrizionista as NutrizionistaSchema






nutrizionista_schema_for_dump = NutrizionistaSchema(only=['id_nutrizionista', 'nome', 'cognome'])



class Nutrizionista(Resource):

   

    @paziente_required()
    @paziente_ns.doc('recupera paziente')
    def get(self):
        id_paziente = get_jwt_identity()
        nutrizionista = NutrizionistaService.get_nutrizionista_by_paziente(id_paziente)
        if nutrizionista:
            return nutrizionista_schema_for_dump.dump(nutrizionista), 200
        return {"message": "nutrizionista non trovato"}, 404
