from django.db import models


class Recognition(models.Model):
    name = models.CharField(max_length=100, null=True)
    id_image = models.ImageField(upload_to='id_images/', null=True)
    extracted_id_image = models.ImageField(upload_to='extracted_images/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return self.name if self.name is not None else "unknown user"


class LiveImage(models.Model):
    image = models.ImageField(upload_to='live_images/')
    recognition = models.ForeignKey(Recognition, on_delete=models.CASCADE, null=True, blank=True)
    is_face_matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.recognition
