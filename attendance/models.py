from django.db import models
from students.models import Student
from lectures.models import Lecture

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecture')

    def __str__(self):
        return f"{self.student.registration_number} | {self.lecture}"