# from flaskr import db
from flaskr.ma import ma
from flaskr.models.patologia import PatologiaModel


class PatologiaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PatologiaModel
        load_instance = True
        include_fk = False