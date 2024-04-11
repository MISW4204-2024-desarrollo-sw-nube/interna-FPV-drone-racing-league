from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import TIMESTAMP, Enum
import enum
import os
import datetime 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql+psycopg2://postgres:1234@database:5432/postgres'
app.config["SECRET_KEY"] = 'your-secret-key'
app.config["UNPROCESSED_FOLDER"] = os.path.join(os.getcwd(), 'unprocessed_videos')
app.config["PROCESSED_FOLDER"] = os.path.join(os.getcwd(), 'processed_videos')
app.config["RESOURCES_FOLDER"] = os.path.join(os.getcwd(), 'res')
app.config["LOGO_FILE"] = os.path.join(app.config["RESOURCES_FOLDER"], 'maxresdefault.jpg')
app_context = app.app_context()
app_context.push()
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

class Status(enum.Enum):
    inprogress = 0
    complete = 1
    incomplete = -1

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(Enum(Status))
    inprogress_file_url = db.Column(db.String(255))
    created_on = db.Column(TIMESTAMP,  
                        default=datetime.datetime.utcnow) 
    updated_at = db.Column(TIMESTAMP,  
                        default=datetime.datetime.utcnow) 
    complete_file_url = db.Column(db.String(255))

class VideoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'status', 'inprogress_file_url', 'complete_file_url')


video_schema = VideoSchema()


