import datetime
import os

from flask import request, jsonify
from sqlalchemy import asc, desc
from werkzeug.utils import secure_filename

from base import app, db, Video, Usuario, Status, celery_app, video_schema, videos_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from google.cloud import storage

@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass

def find_user_account_by_id(user_id):
   return Usuario.query.filter(Usuario.id == user_id).first()

def is_userid_invalid(user_id):
    if user_id is None:
         return "Invalid token. Please provide another token.", 400

    if find_user_account_by_id(user_id) is None:
        return "User does not exist. Please provide another token.", 400

@app.route('/api/tasks', methods=['POST'])
@jwt_required()
def upload_video():
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
       return is_userid_invalid(user_id)

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

    # Upload to GCS bucket
    bucket_name = 'ifpv-videos'
    source_file_name = os.path.join(current_unprocessed_folder, filename_with_timestamp)
    destination_blob_name = f"unprocessed_videos/{filename_with_timestamp}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

    video = Video(
        status=Status.uploaded,
        uploaded_file_url=os.path.join(
            current_unprocessed_folder,
            filename_with_timestamp
        ),
        created_on=datetime.datetime.now(),
        owner_id = user_id
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
@jwt_required()
def get_video(id):
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
       return is_userid_invalid(user_id)

    if id is None:
        return jsonify(error="No id provided"), 400
    video = db.session.query(Video).filter(Video.id == id, Video.owner_id == user_id).first()
    if video is None:
        return "", 404
    return video_schema.dump(video)


@app.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_video_list():
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
       return is_userid_invalid(user_id)

    max_value = int(request.args.get('max', 10))
    order_value = int(request.args.get('order', 0))

    order_func = desc if order_value == 1 else asc
    videos = db.session.query(Video).filter(Video.status != Status.deleted, Video.owner_id == user_id).order_by(order_func(Video.id)).limit(max_value)

    return videos_schema.dump(videos.all())


@app.route('/api/tasks/<id>', methods=['DELETE'])
@jwt_required()
def delete_video(id):
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
       return is_userid_invalid(user_id)

    video = db.session.query(Video).filter(Video.id == id, Video.owner_id == user_id).first()
    if video is None:
        return "", 404

    if video.status == Status.deleted:
        return jsonify(error=f"Video with id:{id} is already deleted"), 400

    # delete the unprocessed and processed files
    try:
        os.remove(video.uploaded_file_url)
        video.uploaded_file_url = None
    except Exception:
        return jsonify(error=f"Error deleting the uploaded video file with id:{id}"), 500

    try:
        os.remove(video.processed_file_url)
        video.processed_file_url = None
    except Exception:
        return jsonify(error=f"Error deleting the processed video file with id:{id}"), 500

    # Update status of the video record
    try:
        video.updated_at = datetime.datetime.now()
        video.status = Status.deleted
        db.session.commit()
        return "", 204
    except Exception:
        return jsonify(error=f"Error deleting the video with id:{id}"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
