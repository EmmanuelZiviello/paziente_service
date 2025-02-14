# from flaskr import db
from F_taste_paziente.ma import ma
from F_taste_paziente.models.allergia import AllergiaModel

class AllergiaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AllergiaModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True