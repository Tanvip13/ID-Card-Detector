import cv2
from mtcnn import MTCNN
import matplotlib.pyplot as plt

def extract_face_from_id_card(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    # Convert the image from BGR to RGB format
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Initialize the MTCNN face detector
    detector = MTCNN()

    # Detect faces in the image
    faces = detector.detect_faces(image_rgb)

    # Loop through the detected faces
    print(faces)
    for face in faces:
        # Get the bounding box coordinates of the face
        x, y, width, height = face['box']
        # Extract the face from the image
        face_image = image_rgb[y:y+height, x:x+width]
        # Display the extracted face
        plt.imshow(face_image)
        plt.axis('off')
        plt.show()

# Specify the path to the ID card image
image_path = 'id_image.jpg'

# Extract and display the face from the ID card
extract_face_from_id_card(image_path)
