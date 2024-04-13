import datetime
import os

from flask import request, jsonify
from sqlalchemy import asc, desc
from werkzeug.utils import secure_filename

from base import app, db, Video, Status, celery_app, video_schema, videos_schema


@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass


@app.route('/api/tasks', methods=['POST'])
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

    video = Video(
        status=Status.uploaded,
        uploaded_file_url=os.path.join(
            current_unprocessed_folder,
            filename_with_timestamp
        ),
        created_on=datetime.datetime.now()
    )
    db.session.add(video)
    db.session.commit()

    args = [
        filename_with_timestamp,
        current_unprocessed_folder,
        current_processed_folder,
        logo_file,
        video.id
    ]

    # Call celery
    procesar_video.apply_async(args=args, queue='batch_videos')

    return jsonify(
        id=video.id,
        message='File uploaded successfully'
    )


@app.route('/api/tasks/<id>', methods=['GET'])
def get_video(id):
    if id is not None:
        video = db.session.query(Video).filter(Video.id == id).first()
        if video is None:
            return "", 404
        return video_schema.dump(video)
    else:
        return "", 404
    
@app.route('/api/tasks', methods=['GET'])
def get_video_list():
    max = int(request.args.get('max', 10))
    order = int(request.args.get('order', 0))

    descending_query = db.session.query(Video).order_by(desc(Video.id)).limit(max)
    videos = descending_query if order == 1 else db.session.query(Video).order_by(asc(Video.id)).limit(max)

    return videos_schema.dump(videos.all())


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
