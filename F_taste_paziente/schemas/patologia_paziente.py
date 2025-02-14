from F_taste_paziente.ma import ma
from F_taste_paziente.models.patologia_paziente import PatologiaPaziente
from marshmallow import fields

class PazientePatologiaSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        meta = PatologiaPaziente
        load_instance = True

    id_patologia = fields.Integer(required=True)
    id_paziente = fields.String(required=True)


