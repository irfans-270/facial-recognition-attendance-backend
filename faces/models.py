from django.db import models
from students.models import Student

class FaceEncoding(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="face_encoding"
    )
    encoding = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FaceEncoding for {self.student.registration_number}"
