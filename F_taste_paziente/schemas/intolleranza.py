# from flaskr import db
from F_taste_paziente.ma import ma
from F_taste_paziente.models.intolleranza import IntolleranzaModel

class IntolleranzaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IntolleranzaModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True