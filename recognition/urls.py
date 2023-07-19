from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_recognition, name='create_recognition'),
    path('id/capture/<int:recognition_id>', views.capture_id_image, name='capture_id_image'),
    path('id/recognition/<int:recognition_id>', views.real_time_recognition, name='real-time-recognition'),
    path('success/', views.success, name='success'),
    path('failed/', views.failed, name='failed'),
    path('recognition_list/', views.recognition_list, name='recognition_list'),
    path('recognition_detail/<int:recognition_id>/', views.recognition_detail, name='recognition_detail'),
    path('download-pdf/<int:recognition_id>/', views.download_pdf, name='download_pdf'),

]
