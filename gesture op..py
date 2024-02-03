import paho.mqtt.client as mqtt
import time
import cv2
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim
import serial

# MQTT configurations
mqttBroker = "127.0.0.1"  # Use the actual IP address of your MQTT broker
mqttTopic = "object_recognition"  # Replace with your desired MQTT topic

client = mqtt.Client("object_recognition")
client.connect(mqttBroker)

# Function to send MQTT message
def send_mqtt_message(message):
    client.publish(mqttTopic, message)

# Function to handle MQTT messages
def on_message(client, userdata, message):
    received_message = str(message.payload.decode("utf-8"))
    print("Received Message:", received_message)

# Set up MQTT subscription
client.subscribe(mqttTopic)
client.on_message = on_message

# Load the pre-trained object detection model (for example, a face)
object_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the reference image of the object
reference_image_path = 'C:\\Users\\admin\\Documents\\Photo (1).jpg'  # Replace with the path to your reference object image
reference_image = cv2.imread(reference_image_path)

# Check if the reference image is loaded successfully
if reference_image is None:
    print(f"Error: Unable to load the reference image. Please check the file path: {reference_image_path}")
else:
    print("Reference image loaded successfully.")
    reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

# Create a VideoCapture object for the webcam
cap = cv2.VideoCapture(0)

# Open a serial connection to Arduino
ser = serial.Serial('COM4', 9600)  # Replace 'COM3' with your Arduino serial port and adjust baud rate

def send_command(command):
    ser.write(command.encode())

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the live webcam feed for verification
    cv2.imshow('Webcam Feed', gray)

    # Detect faces in the live webcam feed
    faces = object_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    print("Detected Faces:", len(faces))

    for (x, y, w, h) in faces:
        # Extract the region of interest (ROI) from the live webcam feed
        roi_gray = gray[y:y+h, x:x+w]

        # Resize the ROI to match the size of the reference object image
        roi_gray_resized = cv2.resize(roi_gray, (reference_gray.shape[1], reference_gray.shape[0]))

        # Compare the two images using structural similarity index (SSI)
        ssi_index, _ = compare_ssim(reference_gray, roi_gray_resized, full=True)
        print("SSI Index:", ssi_index)

        # Set a threshold for similarity
        similarity_threshold = 0.7

        # Move the threshold comparison inside the loop
        if ssi_index > (1 - similarity_threshold):
            # Draw a green rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Send 'True' to MQTT when the reference image matches
            send_mqtt_message('True')
        else:
            # Draw a red rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

            # Send 'False' to MQTT
            send_mqtt_message('False')

    # Visualize reference image and webcam frame
    cv2.imshow('Object Recognition', frame)

    if cv2.waitKey(1) == 27:
        send_command('0')  # Send a termination command to Arduino before exiting
        break

cap.release()
cv2.destroyAllWindows()
