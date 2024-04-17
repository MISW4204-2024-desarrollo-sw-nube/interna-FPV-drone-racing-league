#!/bin/bash
celery -A async_video_processor.celery worker -Q batch_videos -E -l info
celery control enable_events