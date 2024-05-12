import base64
import datetime
import json
import os
import time


from base import Status, Video, app, db
from flask import request
from google.cloud import storage
from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips

secretKey = os.environ['PUBSUB_VERIFICATION_TOKEN']

def are_valid_parameters(args):
    if args is None:
         return 'Invalid parameters. Please provide valid arguments.', 400
    
    if "filename_with_timestamp" not in args:
        return 'Invalid parameters. Please provide valid a filename_with_timestamp.', 400

    if "current_unprocessed_folder" not in args:
        return 'Invalid parameters. Please provide valid a current_unprocessed_folder.', 400
        
    if "current_processed_folder" not in args:
        return 'Invalid parameters. Please provide valid a current_processed_folder.', 400

    if "logo_file" not in args:
        return 'Invalid parameters. Please provide valid a logo_file.', 400

    if "video_id" not in args:
        return 'Invalid parameters. Please provide valid a video_id.', 400

    if "cloud_storage_bucket" not in args:
        return 'Invalid parameters. Please provide valid a cloud_storage_bucket.', 400

    if "proccessedVideosName" not in args:
        return 'Invalid parameters. Please provide valid a proccessedVideosName.', 400

    if "unproccessedVideosName" not in args:
        return 'Invalid parameters. Please provide valid a unproccessedVideosName.', 400

    if "user_id" not in args:
        return 'Invalid parameters. Please provide valid a user_id.', 400

def procesar_video(
    unprocessed_file_name,
    current_unprocessed_folder,
    current_processed_folder,
    logo_file_path,
    video_id,
    cloud_storage_bucket,
    proccessedVideosName,
    unproccessedVideosName,
    user_id,
):

    start_time = time.time()
    unprocessed_file_path = os.path.join(
        current_unprocessed_folder, unprocessed_file_name
    )
    processed_file_path = None
    try:
        # Download unprocessed from GCS bucket
        app.logger.info("Started downloading video...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(cloud_storage_bucket)

        unprocessed_blob_name = (
            f"{unproccessedVideosName}/{user_id}/{unprocessed_file_name}"
        )
        blob = bucket.blob(unprocessed_blob_name)
        os.makedirs(current_unprocessed_folder, exist_ok=True)
        blob.download_to_filename(unprocessed_file_path)
        app.logger.info("Downloaded video")

        # Process the video
        app.logger.info("Started processing video...")
        unprocessed_video = VideoFileClip(unprocessed_file_path)

        # Shorten the video if it's longer than 20 seconds
        if unprocessed_video.duration > 20:
            unprocessed_video = unprocessed_video.subclip(0, 20)
        app.logger.info("Cut video")

        # Add the IDRL logo at the beginning and end of the video
        idrl_logo = ImageClip(logo_file_path, duration=1)
        processed_video = concatenate_videoclips(
            [idrl_logo, unprocessed_video, idrl_logo]
        )

        # Change the aspect ratio to 16:9
        processed_video = processed_video.resize(height=720)
        # Resize height to 720p
        app.logger.info("Resized video")
        processed_video = processed_video.crop(
            x_center=processed_video.w / 2,
            y_center=processed_video.h / 2,
            width=1280,
            height=720,
        )  # Crop to 16:9
        app.logger.info("Cropped video")

        # Save the final video
        processed_file_name = "processed_" + unprocessed_file_name
        processed_file_path = os.path.join(
            current_processed_folder, processed_file_name
        )
        os.makedirs(current_processed_folder, exist_ok=True)
        processed_video.write_videofile(processed_file_path)
        app.logger.info(f"Processed video: {processed_file_path}")

        # Upload to GCS bucket
        destination_blob_name = (
            f"{proccessedVideosName}/{user_id}/{processed_file_name}"
        )
        blob = bucket.blob(destination_blob_name)
        with open(processed_file_path, "rb") as file:
            app.logger.info("Started uploading video...")
            blob.upload_from_file(file)
            app.logger.info("Uploaded video")

        db.session.query(Video).filter(Video.id == video_id).update(
            {
                Video.updated_at: datetime.datetime.now(),
                Video.status: Status.processed,
                Video.processed_file_url: destination_blob_name,
            }
        )
        db.session.commit()
        app.logger.info(f"Saved video in db: {processed_file_path} with id: {video_id}")
        db.session.close()
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Tiempo de procesamiento: {processing_time} segundos")
    except Exception as ex:
        db.session.query(Video).filter(Video.id == video_id).update(
            {Video.status: Status.incomplete, Video.processed_file_url: None}
        )
        db.session.commit()
        app.logger.error(f"{ex}")
    try:
        # Remove files from local storage
        os.remove(unprocessed_file_path)
        os.remove(processed_file_path)
        db.session.close()
    except Exception as e:
        db.session.close()
        app.logger.error(f"Error removing files: {e}")

@app.route("/api/process-videos", methods=["POST"])
def upload_video():
    if (request.args.get('token', '') != secretKey):
        return 'Invalid request', 400

    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])
    data = json.loads(str(payload, 'utf-8'))

    validation = are_valid_parameters(data)

    if validation is not None:
        return validation

    procesar_video(
        data["filename_with_timestamp"],
        data["current_unprocessed_folder"],
        data["current_processed_folder"],
        data["logo_file"],
        int(data["video_id"]),
        data["cloud_storage_bucket"],
        data["proccessedVideosName"],
        data["unproccessedVideosName"],
        int(data["user_id"])
    )

    # Returning any 2xx status indicates successful receipt of the message.
    return 'OK', 200


if __name__ == "__main__":
    app.run(host="0.0.0.0")