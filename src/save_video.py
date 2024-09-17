# src/save_video.py
import cv2
import os
import time
from datetime import datetime
from src.config import VIDEO_SAVE_DIR

def save_video_clip(video_capture, duration=10, fps=30):
    if not os.path.exists(VIDEO_SAVE_DIR):
        os.makedirs(VIDEO_SAVE_DIR)

    # Create video file name with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    video_path = os.path.join(VIDEO_SAVE_DIR, f'clip_{timestamp}.avi')

    # Get frame size
    frame_width = int(video_capture.get(3))
    frame_height = int(video_capture.get(4))

    # Define the codec and initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = video_capture.read()
        if not ret:
            break
        out.write(frame)

    out.release()
    return video_path
