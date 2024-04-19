from flask import Flask
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics
from marshmallow_enum import EnumField
from sqlalchemy import TIMESTAMP, Enum
import datetime
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql+psycopg2://postgres:1234@database:5432/postgres'
app.config["JWT_SECRET_KEY"] = "1234"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app_context = app.app_context()
app_context.push()

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
metrics = PrometheusMetrics(app)
api = Api(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    useremail = db.Column(db.String(255))
    username = db.Column(db.String(255))
    userpassword = db.Column(db.String(255))

class Status(enum.Enum):
    incomplete = "incomplete"
    uploaded = "uploaded"
    processed = "processed"
    deleted = "deleted"

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(Enum(Status))
    uploaded_file_url = db.Column(db.String(255))
    created_on = db.Column(TIMESTAMP,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(TIMESTAMP,
                           default=datetime.datetime.utcnow)
    processed_file_url = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'useremail', 'username', 'userpassword')

class VideoSchema(ma.SQLAlchemyAutoSchema):
    status = EnumField(Status, by_value=True)

    class Meta:
        model = Video

usuario_schema = UsuarioSchema()
video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)