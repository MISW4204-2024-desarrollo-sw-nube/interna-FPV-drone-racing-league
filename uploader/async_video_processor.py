import datetime
import os

import celeryconfig
from base import Status, Video, db
from celery import Celery
from celery.utils.log import get_task_logger
from google.cloud import storage
from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips

celery = Celery(
    "async_video_processor",
)
celery.config_from_object(celeryconfig)
logger = get_task_logger("async_video_processor")


@celery.task(name="procesar_video")
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
    unprocessed_file_path = os.path.join(
        current_unprocessed_folder, unprocessed_file_name
    )
    processed_file_path = None
    try:
        # Download unprocessed from GCS bucket
        logger.info("Started downloading video...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(cloud_storage_bucket)

        unprocessed_blob_name = (
            f"{unproccessedVideosName}/{user_id}/{unprocessed_file_name}"
        )
        blob = bucket.blob(unprocessed_blob_name)
        os.makedirs(current_unprocessed_folder, exist_ok=True)
        blob.download_to_filename(unprocessed_file_path)
        logger.info("Downloaded video")

        # Process the video
        logger.info("Started processing video...")
        unprocessed_video = VideoFileClip(unprocessed_file_path)

        # Shorten the video if it's longer than 20 seconds
        if unprocessed_video.duration > 20:
            unprocessed_video = unprocessed_video.subclip(0, 20)
        logger.info("Cut video")

        # Add the IDRL logo at the beginning and end of the video
        idrl_logo = ImageClip(logo_file_path, duration=1)
        processed_video = concatenate_videoclips(
            [idrl_logo, unprocessed_video, idrl_logo]
        )

        # Change the aspect ratio to 16:9
        processed_video = processed_video.resize(height=720)
        # Resize height to 720p
        logger.info("Resized video")
        processed_video = processed_video.crop(
            x_center=processed_video.w / 2,
            y_center=processed_video.h / 2,
            width=1280,
            height=720,
        )  # Crop to 16:9
        logger.info("Cropped video")

        # Save the final video
        processed_file_name = "processed_" + unprocessed_file_name
        processed_file_path = os.path.join(
            current_processed_folder, processed_file_name
        )
        os.makedirs(current_processed_folder, exist_ok=True)
        processed_video.write_videofile(processed_file_path)
        logger.info(f"Processed video: {processed_file_path}")

        # Upload to GCS bucket
        destination_blob_name = (
            f"{proccessedVideosName}/{user_id}/{processed_file_name}"
        )
        blob = bucket.blob(destination_blob_name)
        with open(processed_file_path, "rb") as file:
            logger.info("Started uploading video...")
            blob.upload_from_file(file)
            logger.info("Uploaded video")

        db.session.query(Video).filter(Video.id == video_id).update(
            {
                Video.updated_at: datetime.datetime.now(),
                Video.status: Status.processed,
                Video.processed_file_url: destination_blob_name,
            }
        )
        db.session.commit()
        logger.info(f"Saved video in db: {processed_file_path} with id: {video_id}")
    except Exception as e:
        db.session.query(Video).filter(Video.id == video_id).update(
            {Video.status: Status.incomplete, Video.processed_file_url: None}
        )
        db.session.commit()
    try:
        # Remove files from local storage
        os.remove(unprocessed_file_path)
        os.remove(processed_file_path)
    except Exception as e:
        logger.error(f"Error removing files: {e}")
