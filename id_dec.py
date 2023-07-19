import cv2
import face_recognition


def is_same_person(live_image_path, id_image_path):
    # Load the live image and the ID card image
    live_image = face_recognition.load_image_file(live_image_path)
    id_image = face_recognition.load_image_file(id_image_path)

    # Detect faces in both images
    live_face_locations = face_recognition.face_locations(live_image)
    id_face_locations = face_recognition.face_locations(id_image)

    # Ensure that a face was detected in both images
    if not live_face_locations or not id_face_locations:
        return False

    # Encode the faces into feature vectors
    live_face_encodings = face_recognition.face_encodings(live_image, live_face_locations)
    id_face_encodings = face_recognition.face_encodings(id_image, id_face_locations)

    # Compare the feature vectors to determine if the faces match
    matches = face_recognition.compare_faces(live_face_encodings, id_face_encodings[0])

    return matches[0]


# Example usage
live_image_path = "./IMG-20230407-WA0000.jpg"
id_image_path = "./Screenshot 2023-04-04 at 12.13.43 PM.png"
result = is_same_person(live_image_path, id_image_path)
print(result)
if result:
    print("The person holding the ID is the same as the person in the photo on the ID.")
else:
    print("The person holding the ID is not the same as the person in the photo on the ID.")
