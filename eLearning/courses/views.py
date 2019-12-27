import logging
from django.shortcuts import render
from django.urls import reverse, resolve
from django.views.generic import ListView, DetailView, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from courses.models import (
    Course,
)

from courses.forms import CourseForm


logger = logging.getLogger('eLearning')


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


# TODO: transfer js code in static file
@method_decorator(login_required, name='dispatch')
class EditCourseView(FormView):
    template_name = "courses/course_edit.html"
    form_class = CourseForm
    model = Course
    extra_context = {"success_message": ""}
    course_instance = None
    pk = None

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs['pk']
        self.course_instance = Course.objects.get(pk=self.pk)
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.course_instance})
        return kwargs

    def get_initial(self):
        self.initial = {
            "name": self.course_instance.name,
            "min_pass_grade": self.course_instance.min_pass_grade,
            "type": self.course_instance.type,
            "status": self.course_instance.status,
            "content": self.course_instance.content,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.extra_context["success_message"] = "Course updated"
            logger.info(f'{request.user} updated course - {self.pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update course - {self.pk}.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['pk'] = self.pk
        kwargs['course_types'] = self.model.COURSE_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        kwargs['type'] = self.course_instance.type
        kwargs['status'] = self.course_instance.status
        # kwargs['action_url'] = 'course_edit'   # 'course_edit pk'# + str(self.pk)
        # kwargs['action_url'] = reverse('course_edit', args=[self.pk])
        # kwargs['action_url'] = resolve(f'courses/{self.pk}/')
        # print(kwargs['action_url'])
        kwargs['view'] = 'edit'
        return kwargs

    def form_valid(self, form):
        form.initial = {
            "name": self.request.POST.get("name"),
            "min_pass_grade": self.request.POST.get("min_pass_grade"),
            "type": self.request.POST.get("type"),
            "status": self.request.POST.get("status"),
            "content": self.request.POST.get("content"),
        }
        form.save()
        return render(self.request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class  CreateCourseView(FormView):
    template_name = "courses/course_edit.html"
    form_class = CourseForm
    model = Course
    pk = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            logger.info(f'{request.user} created course - {self.pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't created course - {self.pk}.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_types'] = self.model.COURSE_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        # kwargs['action_url'] = 'course_create'
        kwargs['view'] = 'create'
        return kwargs

    def form_valid(self, form):
        course = form.save()
        pk = course.pk
        success_url = reverse('course_edit', kwargs={'pk': pk})
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        form.initial = {
            "name": self.request.POST.get("name"),
            "min_pass_grade": self.request.POST.get("min_pass_grade"),
            "type": self.request.POST.get("type"),
            "status": self.request.POST.get("status"),
            "content": self.request.POST.get("content"),
        }
        return self.render_to_response(self.get_context_data(form=form))
