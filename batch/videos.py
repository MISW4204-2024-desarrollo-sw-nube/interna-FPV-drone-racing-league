import os
from celery import Celery
from base import app
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
from werkzeug.utils import secure_filename

celery = Celery(__name__, broker='redis://redis-broker:6379/0')

@celery.task(name="procesar_video")
def procesar_video(file):
    filename = secure_filename(file.filename)

    # Create directory if not exists
    os.makedirs(app.config['UNPROCESSED_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

    file.save(os.path.join(app.config['UNPROCESSED_FOLDER'], filename))

    # TODO: process the video in a separate function, We should use a task queue like Celery for this. this function is blocking and will not scale well

    # Process the video
    clip = VideoFileClip(os.path.join(app.config['UNPROCESSED_FOLDER'], filename))

    # Shorten the video if it's longer than 20 seconds
    if clip.duration > 20:
        clip = clip.subclip(0, 20)

    # Add images at the beginning and end of the video
    img_clip = ImageClip(os.path.join(os.getcwd(), 'res', 'maxresdefault.jpg'), duration=1)
    final_clip = concatenate_videoclips([img_clip, clip, img_clip])

    # Change the aspect ratio to 16:9
    final_clip = final_clip.resize(height=720)  # Resize height to 720p
    final_clip = final_clip.crop(x_center=final_clip.w / 2, y_center=final_clip.h / 2, width=1280,
                                 height=720)  # Crop to 16:9

    # Save the final video
    final_clip.write_videofile(os.path.join(app.config['PROCESSED_FOLDER'], 'final_' + filename))