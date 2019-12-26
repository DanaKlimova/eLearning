from collections import namedtuple

from django.shortcuts import render

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
        ).order_by('-course__rating')[:5]
        current_courses = NamedCourses(
            'Current courses',
            [enrollment.course for enrollment in current_course_enrollments]
        )

        users_courses = NamedCourses('Users courses', (
            Course.objects.filter(type='pbl', owner_type='usr').order_by('-rating')[:5]
        ).union(
            user.individual_courses.filter(owner_type='usr').order_by('-rating')[:5]
        ))

        starred_courses = NamedCourses(
            'Starred courses',
            user.favorite_courses.order_by('-rating')[:5]
        )

        last_completed_course_enrollments = user.courseenrollment_set.filter(
            finished_at__isnull=False
        ).order_by('-course__rating')[:5]
        last_completed_courses = NamedCourses(
            'Last completed courses',
            [enrollment.course for enrollment in last_completed_course_enrollments]
        )

        recomended_courses = NamedCourses(
            'Recomended',
            Course.objects.order_by('-rating')[:5]
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
