from flaskr.ma import ma
from flaskr.models.log_consensi import LOGConsensi
from marshmallow import fields

class LogConsensiSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = LOGConsensi
        load_instance = True

    
    valore = fields.Boolean(required = True)
    id_paziente = fields.String(required = True)
    tipologia = fields.String(required = True)

