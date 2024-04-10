
from flask import request
from base import app
from celery import Celery

celery_app = Celery("videos", broker='redis://redis-broker:6379/0')

@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    procesar_video.apply_async(args=file, queue='logs')
    return 'File uploaded and processed successfully'