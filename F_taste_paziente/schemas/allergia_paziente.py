from F_taste_paziente.ma import ma
from F_taste_paziente.models.allergia_paziente import AllergiaPaziente
from marshmallow import fields

class PazienteAllergiaSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        meta = AllergiaPaziente
        load_instance = True

    id_patologia = fields.Integer(required=True)
    id_paziente = fields.String(required=True)
