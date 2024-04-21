
import datetime
import enum
import os
import celeryconfig

from celery import Celery
from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow_enum import EnumField
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TIMESTAMP, Enum
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics

database = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
port = os.environ['POSTGRES_PORT']
secretKey = os.environ['JWT_SECRET_KEY']
root = os.environ['ROOT']
unproccessedVideosName = os.environ['UNPROCCESSED_VIDEOS_NAME']
proccessedVideosName = os.environ['PROCESSED_VIDEOS_NAME']

database_url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config["SECRET_KEY"] = 'your-secret-key'
app.config["JWT_SECRET_KEY"] = secretKey
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["ROOT"] = root
app.config["UNPROCESSED_FOLDER"] = os.path.join(
    app.config["ROOT"],
    unproccessedVideosName
)
app.config["PROCESSED_FOLDER"] = os.path.join(
    app.config["ROOT"],
    proccessedVideosName
)
app.config["RESOURCES_FOLDER"] = os.path.join(app.config["ROOT"], 'res')
app.config["LOGO_FILE"] = os.path.join(
    app.config["RESOURCES_FOLDER"],
    'maxresdefault.jpg'
)
app_context = app.app_context()
app_context.push()


db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
metrics = PrometheusMetrics(app)
jwt = JWTManager(app)

celery_app = Celery(
    "async_video_processor",
)
celery_app.config_from_object(celeryconfig)

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