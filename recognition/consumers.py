import base64
import json
import numpy as np
import concurrent.futures

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async

from .models import Recognition, LiveImage  # Import your Recognition model
import asyncio
import face_recognition
import cv2
from PIL import Image
from io import BytesIO


class IdCardImageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    def get_face_locations(self, image):
        # This function will be executed in a separate thread
        return face_recognition.face_locations(image)

    @database_sync_to_async
    def save_ext_id_image(self, image, recognition_obj):
        recognition_obj.extracted_id_image = image
        recognition_obj.save()
        return recognition_obj

    async def extract_face_sync(self, id_image, recognition_obj):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_face_locations, id_image)
            face_locations = future.result()  #
        if face_locations:
            top, right, bottom, left = face_locations[0]
            face_image = id_image[top:bottom, left:right]
            face_image = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
            pil_image = Image.fromarray(face_image)
            img_io = BytesIO()
            pil_image.save(img_io, format='JPEG')
            # Use sync_to_async to perform the synchronous database operation
            img_content_file = ContentFile(img_io.getvalue(), name="face.jpg")
            await self.save_ext_id_image(img_content_file, recognition_obj)
            return recognition_obj.id
        return None

    @database_sync_to_async
    def get_rec_obj(self, rec_id):
        recognition_obj = get_object_or_404(Recognition, id=rec_id)
        return recognition_obj

    @database_sync_to_async
    def save_id_image(self, image, recognition_obj):
        recognition_obj.id_image = image
        recognition_obj.save()
        return recognition_obj

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        image_data = text_data_json['id_image']
        rec_id = text_data_json['rec_id']
        recognition_obj = await self.get_rec_obj(rec_id)

        # Remove header information from base64 image data
        image_data = image_data.split(',')[1]

        # Convert base64 to binary
        image_binary = base64.b64decode(image_data)
        # Run the asynchronous coroutine using asyncio.run
        nparr = np.frombuffer(image_binary, np.uint8)

        # Decode the NumPy array to an image (ndarray)
        img_ndarray = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        is_success, img_buffer = cv2.imencode(".jpg", img_ndarray)
        if is_success:
            img_bytes = img_buffer.tobytes()
            # Create a ContentFile from the image bytes
            img_content_file = ContentFile(img_bytes, name="captured_image.jpg")
            await self.save_id_image(img_content_file, recognition_obj)
        await asyncio.sleep(1)
        face_id = await self.extract_face_sync(img_ndarray, recognition_obj)

        # Send a response back to the client
        await self.send(text_data=json.dumps({'status': 'success', 'message': 'Image processed and saved.', 'face_id': face_id}))


class ImageRecognitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def get_rec_obj(self, rec_id):
        recognition_obj = get_object_or_404(Recognition, id=rec_id)
        return recognition_obj

    def get_face_locations(self, live_image, id_image):
        # This function will be executed in a separate thread
        # Detect faces in both images
        live_face_locations = face_recognition.face_locations(live_image)
        id_face_locations = face_recognition.face_locations(id_image)
        return live_face_locations, id_face_locations

    def get_live_face_encodings(self, live_image, live_face_locations):
        # This function will be executed in a separate thread
        # Detect faces in both images
        live_face_encodings = face_recognition.face_encodings(live_image, live_face_locations)
        return live_face_encodings

    def get_id_face_encodings(self, id_image, id_face_locations):
        # This function will be executed in a separate thread
        # Detect faces in both images
        live_face_encodings = face_recognition.face_encodings(id_image, id_face_locations)
        return live_face_encodings

    async def is_same_person(self, live_image_path, id_image_path):
        # Load the live image and the ID card image
        live_image = face_recognition.load_image_file(live_image_path)
        id_image = face_recognition.load_image_file(id_image_path)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_face_locations, live_image, id_image)
            live_face_locations, id_face_locations = future.result()  #

        # Ensure that a face was detected in both images
        if not live_face_locations or not id_face_locations:
            return False

        # Encode the faces into feature vectors
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(self.get_live_face_encodings, live_image, live_face_locations)
            future2 = executor.submit(self.get_id_face_encodings, id_image, id_face_locations)
            live_face_encodings = future1.result()  #
            id_face_encodings = future2.result()  #

        # Compare the feature vectors to determine if the faces match
        matches = face_recognition.compare_faces(live_face_encodings, id_face_encodings[0])

        return matches[0]

    @database_sync_to_async
    def update_rec_obj(self, is_success, recognition_obj):
        recognition_obj.is_success = is_success
        recognition_obj.save()
        return recognition_obj

    @database_sync_to_async
    def create_live_img_obj(self, live_image, recognition_obj):
        live_img = LiveImage.objects.create(image=live_image, recognition=recognition_obj)
        return live_img

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        image_data = text_data_json['live_image']
        rec_id = text_data_json['rec_id']
        recognition_obj = await self.get_rec_obj(rec_id)

        # Remove header information from base64 image data
        image_data = image_data.split(',')[1]

        # Convert base64 to binary
        image_binary = base64.b64decode(image_data)
        # Run the asynchronous coroutine using asyncio.run
        nparr = np.frombuffer(image_binary, np.uint8)

        # Decode the NumPy array to an image (ndarray)
        img_ndarray = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        is_success, img_buffer = cv2.imencode(".jpg", img_ndarray)
        numpy_bool = np.bool_(False)
        python_bool = numpy_bool.item()
        if is_success:
            img_bytes = img_buffer.tobytes()
            # Create a ContentFile from the image bytes
            img_content_file = ContentFile(img_bytes, name="live_image.jpg")
            live_image = await self.create_live_img_obj(img_content_file, recognition_obj)
            await asyncio.sleep(1)
            is_recognised = await self.is_same_person(live_image.image, recognition_obj.id_image)
            await self.update_rec_obj(is_recognised, recognition_obj)

            # Send a response back to the client
            numpy_bool = np.bool_(is_recognised)
            python_bool = numpy_bool.item()
            await self.send(text_data=json.dumps({'status': 'success',
                                                  'message': 'Image Recognition Done..',
                                                  'is_recognised': python_bool}))

        await self.send(text_data=json.dumps({'status': 'fail', 'message': 'Image failed..', 'is_recognised': python_bool}))
