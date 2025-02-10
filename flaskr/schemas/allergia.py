# from flaskr import db
from flaskr.ma import ma
from flaskr.models.allergia import AllergiaModel

class AllergiaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AllergiaModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True