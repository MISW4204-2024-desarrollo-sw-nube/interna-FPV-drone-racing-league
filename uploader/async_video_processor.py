import datetime
import os

from celery import Celery
from celery.utils.log import get_task_logger
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip

from base import Status, Video, db

celery = Celery(
    "async_video_processor",
    broker='redis://broker:6379/0',
    worker_send_task_events=True,
    task_send_sent_event=True
)
logger = get_task_logger("async_video_processor")


@celery.task(name="procesar_video")
def procesar_video(
    unprocessed_file_name,
    current_unprocessed_folder,
    current_processed_folder,
    logo_file_path,
    video_id
):
    try:
        # Process the video
        logger.info("Started processing video...")
        unprocessed_video = VideoFileClip(os.path.join(
            current_unprocessed_folder,
            unprocessed_file_name)
        )

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
        processed_video = processed_video.resize(
            height=720
        )
        # Resize height to 720p
        logger.info("Resized video")
        processed_video = processed_video.crop(
            x_center=processed_video.w / 2,
            y_center=processed_video.h / 2,
            width=1280,
            height=720
        )  # Crop to 16:9
        logger.info("Cropped video")

        # Save the final video
        processed_file_name = os.path.join(
            current_processed_folder,
            'processed_' + unprocessed_file_name
        )
        processed_video.write_videofile(processed_file_name)
        logger.info(f"Processed video: {processed_file_name}")

        db.session.query(Video).filter(Video.id == video_id).update(
            {Video.updated_at: datetime.datetime.now(), Video.status: Status.processed,
             Video.processed_file_url: processed_file_name}
        )
        db.session.commit()
        logger.info(
            f"Saved video in db: {processed_file_name} with id: {video_id}")
    except Exception:
        db.session.query(Video).filter(Video.id == video_id).update(
            {Video.status: Status.incomplete, Video.processed_file_url: None}
        )
        db.session.commit()
