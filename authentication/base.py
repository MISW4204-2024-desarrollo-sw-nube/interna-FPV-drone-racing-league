from flask import Flask
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql+psycopg2://postgres:1234@database:5432/postgres'
app.config["JWT_SECRET_KEY"] = "1234"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app_context = app.app_context()
app_context.push()

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
api = Api(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    useremail = db.Column(db.String(255))
    username = db.Column(db.String(255))
    userpassword = db.Column(db.String(255))

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'useremail', 'username', 'userpassword')

usuario_schema = UsuarioSchema()
