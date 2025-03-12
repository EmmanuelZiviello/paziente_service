from F_taste_paziente.ma import ma
# from flaskr import db
from F_taste_paziente.models.nutrizionista import NutrizionistaModel
from marshmallow import fields

class NutrizionistaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NutrizionistaModel
        load_instance = True
        # sqla_session = db.session