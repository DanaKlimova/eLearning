from collections import namedtuple

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from courses.models import Course

# TODO: think about course ordering.
def home(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        NamedCourses = namedtuple('NamedCourses', [
            'name',
            'courses',
        ])

        current_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=True
        ).order_by('course__rating')[:6]
        current_courses = NamedCourses(
            'Current courses',
            [enrollment.course for enrollment in current_course_enrollments]
        )

        users_courses = NamedCourses('Users courses', (
            Course.objects.filter(type='pbl', owner_type='usr', status='rdy')[:6]
        ).union(
            user.individual_courses.filter(owner_type='usr', status='rdy')[:6]
        ).order_by('rating'))

        starred_courses = NamedCourses(
            'Starred courses',
            user.favorite_courses.order_by('rating')[:6]
        )

        last_completed_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=False
        ).order_by('course__rating')[:6]
        last_completed_courses = NamedCourses(
            'Last completed courses',
            [enrollment.course for enrollment in last_completed_course_enrollments]
        )

        recomended_courses = NamedCourses(
            'Recomended',
            Course.objects.filter(type='pbl', status='rdy').order_by('rating')[:6]
        )

        context['courses_set'] = [
            current_courses,
            users_courses,
            starred_courses,
            last_completed_courses,
            recomended_courses,
        ]
        context['columns'] = 3
    else:
        pass

    return render(request, "main/home.html", context)


@login_required
def current_courses(request):
    if request.method == "GET":
        context = {}

        user = request.user
        current_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=True
        ).order_by('-course__rating')

        current_courses = [course_enrollment.course for course_enrollment in current_course_enrollments]

        context["courses"] = current_courses
        context["courses_type"] = "current"
    return render(request, "main/category_courses.html", context)


@login_required
def users_courses(request):
    if request.method == "GET":
        context = {}

        user = request.user

        users_courses = (Course.objects.filter(
            type='pbl',
            owner_type='usr',
            status='rdy')
            ).union(
            user.individual_courses.filter(
                owner_type='usr',
                status='rdy'
            )).order_by('rating')

        context["courses"] = users_courses
        context["courses_type"] = "users"
    return render(request, "main/category_courses.html", context)
