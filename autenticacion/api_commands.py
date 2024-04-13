import datetime
import os

from flask import request, jsonify
from werkzeug.utils import secure_filename

from base import app, db, Video, Status
from base import celery_app


@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass

@app.route('/api-commands/users/signup', methods=['POST'])
def upload_video():
   email = request.json['email']
   username = request.json['username']
   password = request.json['username']

   if email is None or username is None or password is None:
       return "Email, username of password are invalid. Please review it.", 400

   return "Success", 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
