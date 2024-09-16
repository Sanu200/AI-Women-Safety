# src/save_video.py
import cv2
import os
from datetime import datetime
from src.config import VIDEO_SAVE_DIR

def save_video_clip(frame, duration=10, fps=20):
    if not os.path.exists(VIDEO_SAVE_DIR):
        os.makedirs(VIDEO_SAVE_DIR)

    # Create video file name with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    video_path = os.path.join(VIDEO_SAVE_DIR, f'clip_{timestamp}.avi')

    # Define the codec and initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    height, width, _ = frame.shape
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for _ in range(duration * fps):  # Save frames for 'duration' seconds
        out.write(frame)

    out.release()
    return video_path