import datetime
import os
from base import app, db, Video, Status
from flask import request, jsonify
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
from werkzeug.utils import secure_filename

@app.route('/api-commands/uploader/upload-video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return 'No file part'

    # Get the current date  and time as a string
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Create the current date folders
    current_unprocessed_folder = os.path.join(app.config['UNPROCESSED_FOLDER'], current_date)
    current_processed_folder = os.path.join(app.config['PROCESSED_FOLDER'], current_date)
    os.makedirs(current_unprocessed_folder, exist_ok=True)
    os.makedirs(current_processed_folder, exist_ok=True)

    # Save the file
    file = request.files['file']
    # TODO: As we are planning to use auth, we should use the user id as a prefix for the filename
    filename = secure_filename(file.filename)
    filename_without_ext = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    filename_with_timestamp = f"{filename_without_ext}_{current_time}{extension}"

    
    # TODO: We need to use the DB container to store the file url with status 'uploaded'
    video = Video(status=Status.uploaded,uploaded_file_url=os.path.join(current_unprocessed_folder, filename_with_timestamp),created_on=datetime.datetime.now())
    db.session.add(video)
    db.session.commit()

    file.save(os.path.join(current_unprocessed_folder, filename_with_timestamp))

    # TODO: process the video in a separate function, We should use a task queue like Celery for this. this function is blocking and will not scale well

    # Process the video
    # it should be updated by the workebr of the broker (Celery, Kafka, Etc)

    unprocessed_video = VideoFileClip(
        os.path.join(current_unprocessed_folder, filename_with_timestamp))

    # Shorten the video if it's longer than 20 seconds
    if unprocessed_video.duration > 20:
        unprocessed_video = unprocessed_video.subclip(0, 20)

    # Add the IDRL logo at the beginning and end of the video
    idrl_logo = ImageClip(app.config["LOGO_FILE"], duration=1)
    processed_video = concatenate_videoclips([idrl_logo, unprocessed_video, idrl_logo])

    # Change the aspect ratio to 16:9
    processed_video = processed_video.resize(height=720)  # Resize height to 720p
    processed_video = processed_video.crop(x_center=processed_video.w / 2, y_center=processed_video.h / 2, width=1280,
                                 height=720)  # Crop to 16:9
    # Save the final video
    processed_video.write_videofile(
        os.path.join(current_processed_folder, 'processed_' + filename_with_timestamp))

    # TODO: We need to update the DB register to status 'processed' and update the file url with the processed file
    video_to_be_updated = Video.query.filter(Video.id == video.id).first()
    if video_to_be_updated is not None:
        video_to_be_updated.processed_file_url = os.path.join(current_processed_folder, 'processed_' + filename_with_timestamp)
        video_to_be_updated.status = Status.processed
        db.session.commit()

    return jsonify(
        id= video_to_be_updated.id,
        message='File uploaded and processed successfully'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc')
