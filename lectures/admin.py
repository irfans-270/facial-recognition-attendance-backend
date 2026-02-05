from django.contrib import admin
from .models import Course, Lecture, Teacher

admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(Teacher)