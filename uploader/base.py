from flask import Flask
from flask_restful import Api
import os


app = Flask(__name__)
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
api = Api(app)
