# from flaskr import db
from flaskr.ma import ma
from flaskr.models.intolleranza import IntolleranzaModel

class IntolleranzaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IntolleranzaModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True