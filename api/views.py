from django.http import JsonResponse
from django.utils import timezone
from lectures.models import Lecture

def current_lecture(request):
    classroom = request.GET.get('classroom')

    if not classroom:
        return JsonResponse(
            {"error": "classroom parameter is required"},
            status=400
        )

    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    lecture = Lecture.objects.filter(
        classroom=classroom,
        date=today,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()

    if not lecture:
        return JsonResponse(
            {"message": "No lecture currently running"},
            status=404
        )

    return JsonResponse({
        "lecture_id": lecture.id,
        "course_code": lecture.course.course_code,
        "course_name": lecture.course.course_name,
        "classroom": lecture.classroom,
        "start_time": lecture.start_time,
        "end_time": lecture.end_time
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json

from lectures.models import Lecture
from students.models import Student
from enrollments.models import Enrollment
from attendance.models import Attendance


@csrf_exempt
def mark_attendance(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)
        classroom = data.get("classroom")
        student_id = data.get("student_id")
    except Exception:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    if not classroom or not student_id:
        return JsonResponse(
            {"error": "classroom and student_id are required"},
            status=400
        )

    # Find current lecture
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    lecture = Lecture.objects.filter(
        classroom=classroom,
        date=today,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()

    if not lecture:
        return JsonResponse(
            {"error": "No lecture currently running"},
            status=404
        )

    # Get student
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse(
            {"error": "Student not found"},
            status=404
        )

    if not student.is_active:
        return JsonResponse(
            {"error": "Student is inactive"},
            status=403
        )

    # Check enrollment
    if not Enrollment.objects.filter(
        student=student,
        course=lecture.course
    ).exists():
        return JsonResponse(
            {"error": "Student not enrolled in this course"},
            status=403
        )

    # Prevent duplicate attendance
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        lecture=lecture
    )

    if not created:
        return JsonResponse(
            {"message": "Attendance already marked"},
            status=200
        )

    return JsonResponse(
        {"message": "Attendance marked successfully"},
        status=201
    )

from django.db.models import Count

def student_attendance_percentage(request, student_id):
    # Get student
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse(
            {"error": "Student not found"},
            status=404
        )

    result = {}

    # Get all courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=student)

    for enrollment in enrollments:
        course = enrollment.course

        # Total lectures conducted for this course
        total_lectures = Lecture.objects.filter(course=course).count()

        # Lectures attended by this student for this course
        attended_lectures = Attendance.objects.filter(
            student=student,
            lecture__course=course
        ).count()

        if total_lectures == 0:
            percentage = 0.0
        else:
            percentage = round(
                (attended_lectures / total_lectures) * 100, 2
            )

        result[course.course_code] = {
            "course_name": course.course_name,
            "attended": attended_lectures,
            "total": total_lectures,
            "percentage": percentage
        }

    return JsonResponse({
        "student": student.registration_number,
        "attendance": result
    })
