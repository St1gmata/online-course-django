from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Course, Enrollment, Choice, Submission


def index(request):
    courses = Course.objects.all()
    return render(request, 'onlinecourse/index.html', {'course_list': courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrolled = False

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    return render(request, 'onlinecourse/course_details_bootstrap.html', {
        'course': course,
        'enrolled': enrolled,
    })


def enroll(request, course_id):
    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return redirect('onlinecourse:course_details', course_id=course.id)


def submit_exam(request, course_id):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    submitted_answer_ids = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answer_ids.extend(request.POST.getlist(key))

    submission = Submission.objects.create(enrollment=enrollment)

    for choice_id in submitted_answer_ids:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)

    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_choice_ids = [choice.id for choice in submission.choices.all()]

    total_grade = 0
    score = 0

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_grade += question.grade
            if question.is_get_score(selected_choice_ids):
                score += question.grade

    return render(request, 'onlinecourse/exam_result.html', {
        'course': course,
        'submission': submission,
        'score': score,
        'total_grade': total_grade,
        'passed': score >= (total_grade / 2 if total_grade else 0),
    })