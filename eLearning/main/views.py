from collections import namedtuple
import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from courses.models import Course, CourseEnrollment
from main.utils import render_to_pdf

logger = logging.getLogger('eLearning')


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
            finished_at__isnull=True,
        ).order_by('course__rating')[:6]
        current_courses = NamedCourses(
            'Current courses',
            [enrollment.course for enrollment in current_course_enrollments
             if enrollment.course.is_visible]
        )

        users_courses = NamedCourses('Users courses', (
            Course.objects.filter(type='pbl', owner_type='usr', status='rdy', is_visible=True)
        ).union(
            user.individual_courses.filter(owner_type='usr', status='rdy', is_visible=True)
        ).order_by('rating')[:6])

        starred_courses = NamedCourses(
            'Starred courses',
            user.favorite_courses.filter(is_visible=True).order_by('rating')[:6]
        )

        last_completed_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=False,
        ).order_by('course__rating')[:6]
        last_completed_courses = NamedCourses(
            'Last completed courses',
            [enrollment.course for enrollment in last_completed_course_enrollments
             if enrollment.course.is_visible]
        )

        recommended_courses = NamedCourses('Recomended', (
            Course.objects.filter(type='pbl', status='rdy', is_visible=True)
            ).union(
            user.individual_courses.filter(status='rdy', is_visible=True)
        ).order_by('rating')[:6])

        context['courses_set'] = [
            current_courses,
            users_courses,
            starred_courses,
            last_completed_courses,
            recommended_courses,
        ]
        context['columns'] = 3
    else:
        pass

    return render(request, "main/home.html", context)


@login_required
def current_courses_view(request):
    if request.method == "GET":
        context = {}

        user = request.user
        current_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=True
        ).order_by('-course__rating')

        current_courses = [course_enrollment.course for course_enrollment in current_course_enrollments
                           if course_enrollment.course.is_visible]

        context["courses"] = current_courses
        context["courses_type"] = "current"
        return render(request, "main/category_courses.html", context)


@login_required
def users_courses_view(request):
    if request.method == "GET":
        context = {}

        user = request.user

        users_courses = (Course.objects.filter(
            type='pbl',
            owner_type='usr',
            status='rdy',
            is_visible=True)
            ).union(
            user.individual_courses.filter(
                owner_type='usr',
                status='rdy',
                is_visible=True,
            )).order_by('rating')

        context["courses"] = users_courses
        context["courses_type"] = "users"
        return render(request, "main/category_courses.html", context)


@login_required
def starred_courses_view(request):
    if request.method == "GET":
        context = {}

        user = request.user
        starred_courses = user.favorite_courses.filter(is_visible=True).order_by('rating')

        context["courses"] = starred_courses
        context["courses_type"] = "starred"
        return render(request, "main/category_courses.html", context)


@login_required
def completed_courses_view(request):
    if request.method == "GET":
        context = {}

        user = request.user

        completed_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=False
        ).order_by('course__rating')

        completed_courses = [enrollment.course for enrollment in completed_course_enrollments
                             if enrollment.course.is_visible]
        is_passed = [enrollment.is_pass for enrollment in completed_course_enrollments
                     if enrollment.course.is_visible]

        context["courses"] = completed_courses
        context["is_passed"] = is_passed
        context["courses_type"] = "completed"
        return render(request, "main/category_courses.html", context)


@login_required
def recommended_courses_view(request):
    if request.method == "GET":
        context = {}

        user = request.user

        recommended_courses = (Course.objects.filter(type='pbl', status='rdy', is_visible=True)
            ).union(
            user.individual_courses.filter(status='rdy', is_visible=True)
        ).order_by('rating')

        context["courses"] = recommended_courses
        context["courses_type"] = "recomended"
    return render(request, "main/category_courses.html", context)


@login_required
def generate_cert_view(request, course_pk):
    if request.method == "GET":
        try:
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            logger.info("Request certificate for not existing course.")
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        try:
            course_enrollment = CourseEnrollment.objects.get(course=course, user=request.user)
        except CourseEnrollment.DoesNotExist:
            logger.info("Request certificate for not existing course enrollment.")
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        else:
            if not course_enrollment.finished_at:
                logger.info("Request certificate for not completed course enrollment.")
                redirect_url = reverse('course_welcom', kwargs={"course_pk": course_enrollment.course.pk})
                return HttpResponseRedirect(redirect_url)
                
            if course_enrollment.grade < course_enrollment.course.min_pass_grade:
                logger.info("Request certificate for failed course enrollment.")
                redirect_url = reverse('course_welcom', kwargs={"course_pk": course_enrollment.course.pk})
                return HttpResponseRedirect(redirect_url)

            full_name = ' '.join([course_enrollment.user.first_name, course_enrollment.user.last_name])
            context = {
                'name': full_name,
                'course': course_enrollment.course.name,
                'date': course_enrollment.finished_at,
            }
            template_name = 'main/certificate.html'
            pdf = render_to_pdf(template_name, request, context)
            return HttpResponse(pdf, content_type='application/pdf')
            # return render(request, template_name, context)


# ERRORS
def error_404(request, exception):
    context = {}
    return render(request, 'main/errors//error_404.html', context)


def error_500(request):
    context = {}
    return render(request, 'main/errors//error_500.html', context)
