import datetime
import os

from base import (
    Status,
    Usuario,
    Video,
    app,
    celery_app,
    db,
    video_schema,
    videos_schema,
)
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from google.cloud import storage
from sqlalchemy import asc, desc
from werkzeug.utils import secure_filename
from google.cloud import pubsub_v1


@celery_app.task(name="procesar_video")
def procesar_video(*args):
    pass


def find_user_account_by_id(user_id):
    user = Usuario.query.filter(Usuario.id == user_id).first()
    db.session.close()
    return user


def is_userid_invalid(user_id):
    if user_id is None:
        return "Invalid token. Please provide another token.", 400

    if find_user_account_by_id(user_id) is None:
        return "User does not exist. Please provide another token.", 400


@app.route("/api/tasks", methods=["POST"])
@jwt_required()
def upload_video():
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
        return is_userid_invalid(user_id)

    unprocessed_folder = app.config["UNPROCESSED_FOLDER"]
    processed_folder = app.config["PROCESSED_FOLDER"]
    logo_file = app.config["LOGO_FILE"]
    cloud_storage_bucket = app.config["CS_BUCKET_NAME"]
    unproccessedVideosName = os.environ["UNPROCCESSED_VIDEOS_NAME"]
    proccessedVideosName = os.environ["PROCESSED_VIDEOS_NAME"]

    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    # Get the current date  and time as a string

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    # Create the current date folders
    current_unprocessed_folder = os.path.join(unprocessed_folder, current_date)
    current_processed_folder = os.path.join(processed_folder, current_date)

    filename = secure_filename(file.filename) if file.filename else None
    if not filename:
        return "Invalid file"

    filename_without_ext = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    filename_with_timestamp = f"{filename_without_ext}_{current_time}{extension}"

    # Upload to GCS bucket
    try:
        destination_blob_name = (
            f"{unproccessedVideosName}/{user_id}/{filename_with_timestamp}"
        )

        storage_client = storage.Client()
        bucket = storage_client.bucket(cloud_storage_bucket)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_file(file)
    except Exception as error :
        db.session.close()
        app.logger.error('Error uploading video to Google Cloud Storage', exc_info=True)
        return jsonify(error="Error uploading video to Google Cloud Storage"), 500

    video = Video(
        status=Status.uploaded,
        uploaded_file_url=destination_blob_name,
        created_on=datetime.datetime.now(),
        owner_id=user_id,
    )
    db.session.begin()
    db.session.add(video)
    db.session.commit()

    # args = [
    #    filename_with_timestamp,
    #    current_unprocessed_folder,
    #    current_processed_folder,
    #    logo_file,
    #    video.id,
    #    cloud_storage_bucket,
    #    proccessedVideosName,
    #    unproccessedVideosName,
    #    user_id
    #]

    args_data = {
        filename_with_timestamp,
        current_unprocessed_folder,
        current_processed_folder,
        logo_file,
        video.id,
        cloud_storage_bucket,
        proccessedVideosName,
        unproccessedVideosName,
        user_id
     }

    #Publish message to a topic
    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path("ifpv-drone-racing-league-003", "ifpv-videos-topic")

    future = publisher.publish(topic_path, args_data)
    print(future.result())
    print(f"Published messages to {topic_path}.")

    # Call celery
    # procesar_video.apply_async(args=args, queue="batch_videos")
    db.session.close()

    return jsonify(id=video.id, message="File uploaded successfully")


@app.route("/api/tasks/<id>", methods=["GET"])
@jwt_required()
def get_video(id):
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
        return is_userid_invalid(user_id)

    if id is None:
        return jsonify(error="No id provided"), 400
    video = (
        db.session.query(Video)
        .filter(Video.id == id, Video.owner_id == user_id)
        .first()
    )
    db.session.close()
    if video is None:
        return "", 404
    return video_schema.dump(video)


@app.route("/api/tasks", methods=["GET"])
@jwt_required()
def get_video_list():
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
        return is_userid_invalid(user_id)

    max_value = int(request.args.get("max", 10))
    order_value = int(request.args.get("order", 0))

    order_func = desc if order_value == 1 else asc
    videos = (
        db.session.query(Video)
        .filter(Video.status != Status.deleted, Video.owner_id == user_id)
        .order_by(order_func(Video.id))
        .limit(max_value)
    )
    db.session.close()

    return videos_schema.dump(videos.all())


@app.route("/api/tasks/<id>", methods=["DELETE"])
@jwt_required()
def delete_video(id):
    user_id = get_jwt_identity()
    if is_userid_invalid(user_id):
        return is_userid_invalid(user_id)

    cloud_storage_bucket = app.config["CS_BUCKET_NAME"]

    video = (
        db.session.query(Video)
        .filter(Video.id == id, Video.owner_id == user_id)
        .first()
    )
    if video is None:
        return "", 404

    if video.status == Status.deleted:
        return jsonify(error=f"Video with id:{id} is already deleted"), 400

    storage_client = storage.Client()
    bucket = storage_client.bucket(cloud_storage_bucket)
    # delete the unprocessed and processed files
    try:
        blob = bucket.blob(video.uploaded_file_url)
        blob.delete()
        video.uploaded_file_url = None
    except Exception:
        db.session.close()
        return jsonify(
            error=f"Error deleting the uploaded video file with id:{id}"
        ), 500

    try:
        blob = bucket.blob(video.processed_file_url)
        blob.delete()
        video.processed_file_url = None
    except Exception:
        db.session.close()
        return jsonify(
            error=f"Error deleting the processed video file with id:{id}"
        ), 500

    # Update status of the video record
    try:
        video.updated_at = datetime.datetime.now()
        video.status = Status.deleted
        db.session.commit()
        db.session.close()
        return "", 204
    except Exception:
        db.session.close()
        return jsonify(error=f"Error deleting the video with id:{id}"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
