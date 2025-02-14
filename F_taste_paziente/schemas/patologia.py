# from flaskr import db
from F_taste_paziente.ma import ma
from F_taste_paziente.models.patologia import PatologiaModel


class PatologiaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PatologiaModel
        load_instance = True
        include_fk = False