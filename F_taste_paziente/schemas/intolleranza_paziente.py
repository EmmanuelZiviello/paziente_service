from F_taste_paziente.ma import ma
from F_taste_paziente.models.intolleranza_paziente import IntolleranzaPaziente
from marshmallow import fields

class PazientePatologiaSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        meta = IntolleranzaPaziente
        load_instance = True

    id_patologia = fields.Integer(required=True)
    id_paziente = fields.String(required=True)


