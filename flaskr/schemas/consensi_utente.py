# from flaskr import db
from flaskr.ma import ma
from flaskr.models.consensi_utente import ConsensiUtenteModel
from marshmallow import fields
class ConsensiUtenteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsensiUtenteModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True

    condivisione_misurazioni_paziente = fields.Boolean(required=True)
    storage_from_Google_fit = fields.Boolean(required=True)
    storage_from_Health_kit = fields.Boolean(required=True)
    management_user_consent = fields.Boolean(required=True)
    statistic_user_consent = fields.Boolean(required=True)
    trainingAI_user_consent= fields.Boolean(required=True)