from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/capture_image/', consumers.IdCardImageConsumer.as_asgi()),
    path('ws/recognize/', consumers.ImageRecognitionConsumer.as_asgi()),
]
