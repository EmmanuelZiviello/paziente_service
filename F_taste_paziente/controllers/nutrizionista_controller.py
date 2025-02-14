from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource,fields
from F_taste_paziente.services.nutrizionista_service import NutrizionistaService
from F_taste_paziente.namespaces import paziente_ns
from F_taste_paziente.utils.jwt_custom_decorators import paziente_required
from F_taste_paziente.db import get_session


class Nutrizionista(Resource):

   

    @paziente_required()
    @paziente_ns.doc('recupera  nutrizionista del paziente')
    def get(self):
        id_paziente = get_jwt_identity()
        return  NutrizionistaService.get_nutrizionista_by_paziente(id_paziente)
