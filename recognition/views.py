from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.templatetags.static import static
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecognitionImageForm, RecognitionNameForm
from .models import LiveImage, Recognition
import face_recognition
import cv2
import pytesseract
from rembg import remove
import numpy as np
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import re

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def create_recognition(request):
    if request.method == 'POST':
        form = RecognitionNameForm(request.POST)
        if form.is_valid():
            rec = form.save()
            return redirect('capture_id_image', rec.id)
    else:
        form = RecognitionNameForm()
    return render(request, 'create_recognition.html', {'form': form})

import asyncio

# Define an asynchronous coroutine to perform face recognition and save to the database
async def extract_face_sync(id_image, recognition_obj):
    loop = asyncio.get_event_loop()
    # Run the synchronous face_recognition.face_locations function in a separate thread
    face_locations = await loop.run_in_executor(None, face_recognition.face_locations, id_image)
    if face_locations:
        top, right, bottom, left = face_locations[0]
        face_image = id_image[top:bottom, left:right]
        face_image = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
        pil_image = Image.fromarray(face_image)
        img_io = BytesIO()
        pil_image.save(img_io, format='JPEG')
        # Use sync_to_async to perform the synchronous database operation
        await sync_to_async(recognition_obj.extracted_id_image.save)('face.jpg', ContentFile(img_io.getvalue()))
        await sync_to_async(recognition_obj.save)()
        return recognition_obj.id
    return None


# Define a synchronous view
def capture_id_image(request, recognition_id):
    if request.method == 'POST':
        recognition_obj = get_object_or_404(Recognition, id=recognition_id)
        form = RecognitionImageForm(request.POST, request.FILES, instance=recognition_obj)
        if form.is_valid():
            form.save()
            id_image = face_recognition.load_image_file(request.FILES['id_image'])

            # Run the asynchronous coroutine using asyncio.run
            face_id = asyncio.run(extract_face_sync(id_image, recognition_obj))
            if face_id:
                return HttpResponse(f"Face extracted and saved with ID: {face_id}")
            return HttpResponse("No face detected in the ID card image.")
        return HttpResponse("Invalid request method.")
    else:
        form = RecognitionImageForm()
    return render(request, 'capture_image.html', {'form': form, "rec_id": recognition_id})


def real_time_recognition(request, recognition_id):
    recognition_obj = get_object_or_404(Recognition, id=recognition_id)

    return render(request, 'real_time_recognition.html', {"recognition_obj": recognition_obj})


def success(request):
    return render(request, 'success.html')


def failed(request):
    return render(request, 'failed.html')


def recognition_list(request):
    recognitions = Recognition.objects.all()
    context = {'recognitions': recognitions}
    return render(request, 'list.html', context)


def recognition_detail(request, recognition_id):
    recognition = get_object_or_404(Recognition, id=recognition_id)
    live_images = LiveImage.objects.filter(recognition=recognition)
    context = {'recognition': recognition, 'live_images': live_images}
    return render(request, 'recognition_detail.html', context)

def download_pdf(request, recognition_id):
    recognition = get_object_or_404(Recognition, id=recognition_id)
    image_url = recognition.id_image
    image = Image.open(image_url.path)
    output = remove(image)
    output = output.crop(output.getbbox())
    # # Convert the image to grayscale
    gray = cv2.cvtColor(np.array(output), cv2.COLOR_RGBA2GRAY)
    text = pytesseract.image_to_string(gray)
    print(text)
    name, id = [x for x in text.split("\n") if x]
    id = re.findall('[0-9]+', id)[0]
    img_width, img_height = image.size
    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(recognition.name)
    
    # Create a PDF canvas
    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12) 


    # Calculate the new y-coordinate to place the image at the top-left corner
    canvas_height = float(p._pagesize[1])
    y = canvas_height - img_height//2

    # Draw the image on the PDF canvas
    p.drawImage(image_url.path, 0, y,  width=img_width//2, height=img_height//2, showBoundary=True)
    p.drawString(10,100, f"Name: {name}")
    p.drawString(10,10, f"Id: {id}")

    # Finish PDF
    p.showPage()
    p.save()

    return response


