import cv2
import time
from src.detection import load_yolo_model, load_gender_model, detect_people_and_classify_gender
from src.alarm import trigger_alarm  # Trigger the alarm sound
from src.save_video import save_video_clip  # Save video clips
from src.email_notification import send_email  # Send email notifications

# Set the dimensions for the video feed
wCam, hCam = 640, 480

def main():
    # Open default camera and set width/height
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, wCam)
    video_capture.set(4, hCam)
    
    yolo_net = load_yolo_model()
    gender_model = load_gender_model()

    # Variables to control recording state and alarm triggers
    alarm_triggered = False
    recording_start_time = None
    pTime = 0

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Detect people and classify gender in the frame
        people, genders = detect_people_and_classify_gender(frame, yolo_net, gender_model)

        # Draw bounding boxes and gender labels on the frame
        for idx, (x, y, w, h) in enumerate(people):
            label = genders[idx] if idx < len(genders) else 'unknown'  # Gender of the detected person
            color = (255, 0, 0) if label == 'Man' else (0, 255, 0)  # Blue for male, green for female
            
            # Draw rectangle and put label on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Trigger the alarm and save the video if conditions are met
        if len(people) > 1 and 'Man' in genders and 'Woman' in genders:
            if not alarm_triggered:
                alarm_triggered = True
                recording_start_time = time.time()

                # Trigger the alarm sound
                trigger_alarm()

                # Save 10-second video clip
                save_video_clip(video_capture, "saved_clips/", duration=10)

                # Send email to authorities with video clip
                send_email("EMAIL_RECEIVER", "Alarm Triggered", "Video clip attached.", "saved_clips/")

        # Calculate and display FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        # Display the real-time feed with bounding boxes and labels
        cv2.imshow('Video Feed', frame)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Reset alarm after 30 seconds
        if alarm_triggered and time.time() - recording_start_time > 30:
            alarm_triggered = False

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
