import logging
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from courses.models import (
    Course,
)


logger = logging.getLogger('eLearning')


# TODO: LOGGING
@method_decorator(login_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    context_object_name = 'course_list'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{self.request.user} viewed course list.')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Course.objects.filter(owner_user=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{self.request.user} viewed course detail.')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)