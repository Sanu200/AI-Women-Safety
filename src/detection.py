import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Load the YOLO model
def load_yolo_model():
    yolov3_cfg = os.path.abspath('C:/Users/sanun/Downloads/ThePRO_JECT 2/models/yolov3.cfg')  # Path to YOLOv3 config file
    yolov3_weights = os.path.abspath('C:/Users/sanun/Downloads/ThePRO_JECT 2/models/yolov3.weights')  # Path to YOLOv3 weights
    net = cv2.dnn.readNetFromDarknet(yolov3_cfg, yolov3_weights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net

# Load the gender classification model
def load_gender_model():
    gender_model_path = os.path.abspath('C:/Users/sanun/Downloads/ThePRO_JECT 2/models/gender_detection.h5')  # Path to gender classification model
    gender_model = load_model(gender_model_path)
    return gender_model

# Detect people using YOLO and classify gender using the gender model
def detect_people_and_classify_gender(frame, yolo_net, gender_model, conf_threshold=0.5, nms_threshold=0.4):
    height, width = frame.shape[:2]
    # YOLO input size
    input_size = (416, 416)
    
    # Create a blob from the frame
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, input_size, swapRB=True, crop=False)
    yolo_net.setInput(blob)

    # Get YOLO output layers
    layer_names = yolo_net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

    # Perform YOLO forward pass
    detections = yolo_net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []


    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold and class_id == 0:  # Class ID 0 is for 'person'
                # Extract the bounding box coordinates
                box = detection[0:4] * np.array([width, height, width, height])
                centerX, centerY, boxW, boxH = box.astype("int")
                x = int(centerX - (boxW / 2))
                y = int(centerY - (boxH / 2))

                boxes.append([x, y, int(boxW), int(boxH)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to eliminate redundant overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Lists to store detected people and their gender classifications
    people = []
    genders = []

    # Handle both cases where indices might be a scalar or a list
    if len(indices) > 0:
        if isinstance(indices[0], list):  # When indices is a list of lists
            indices = [i[0] for i in indices]

    for i in indices:
        x, y, w, h = boxes[i]
        people.append((x, y, w, h))

        # Crop the region of interest (ROI) for gender classification
        roi = frame[y:y + h, x:x + w]
        if roi.size > 0:
                # Resize the ROI to the size expected by the gender model (e.g., 96x96) and preprocess
                roi_resized = cv2.resize(roi, (96, 96))
                roi_array = img_to_array(roi_resized)
                roi_array = np.expand_dims(roi_array, axis=0)
                roi_array /= 255.0  # Normalize the image

                # Use the gender model's predict method
                gender_preds = gender_model.predict(roi_array)

                # Interpret the gender prediction
                gender = "man" if gender_preds[0][0] > gender_preds[0][1] else "woman"
                genders.append(gender)

    return people, genders