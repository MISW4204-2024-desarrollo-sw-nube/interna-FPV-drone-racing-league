import base64
import datetime
import os

from celery import Celery
from flask import request
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
from werkzeug.utils import secure_filename

from base import app

celery_app = Celery("videos", broker='redis://broker:6379/0')


@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass


@app.route('/api-commands/uploader/upload-video', methods=['POST'])
def upload_video():

    unprocessed_folder = app.config['UNPROCESSED_FOLDER']
    processed_folder = app.config['PROCESSED_FOLDER']
    logo_file = app.config["LOGO_FILE"]

    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # Get the current date  and time as a string

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the current date folders
    current_unprocessed_folder = os.path.join(unprocessed_folder, current_date)
    current_processed_folder = os.path.join(processed_folder, current_date)
    os.makedirs(current_unprocessed_folder, exist_ok=True)
    os.makedirs(current_processed_folder, exist_ok=True)

    filename = secure_filename(file.filename) if file.filename else None
    if not filename:
        return 'Invalid file'

    filename_without_ext = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    filename_with_timestamp = f"{filename_without_ext}_{current_time}{extension}"

    # Save the file
    file.save(os.path.join(current_unprocessed_folder, filename_with_timestamp))
    file.close()

    args = [
        filename_with_timestamp,
        current_unprocessed_folder,
        current_processed_folder,
        logo_file
    ]
    print(args)

    # Call celery
    procesar_video.apply_async(args=args, queue='batch_videos')
    # TODO: We need to use the DB container to store the file url with status 'unprocessed'

    return 'File uploaded and processed successfully'


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
