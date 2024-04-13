
import datetime
import enum
import os

from celery import Celery
from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow_enum import EnumField
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TIMESTAMP, Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@database:5432/postgres'
app.config["SECRET_KEY"] = 'your-secret-key'
app.config["ROOT"] = '/shared'
app.config["UNPROCESSED_FOLDER"] = os.path.join(
    app.config["ROOT"],
    'unprocessed_videos'
)
app.config["PROCESSED_FOLDER"] = os.path.join(
    app.config["ROOT"],
    'processed_videos'
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

celery_app = Celery("async_video_processor", broker='redis://broker:6379/0')


class Status(enum.Enum):
    incomplete = "incomplete"
    uploaded = "uploaded"
    processed = "processed"


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(Enum(Status))
    uploaded_file_url = db.Column(db.String(255))
    created_on = db.Column(TIMESTAMP,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(TIMESTAMP,
                           default=datetime.datetime.utcnow)
    processed_file_url = db.Column(db.String(255))


class VideoSchema(ma.SQLAlchemyAutoSchema):
    status = EnumField(Status, by_value=True)

    class Meta:
        model = Video


video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
