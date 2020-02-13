import logging
from datetime import date
import json
import math

from django.shortcuts import render, get_object_or_404
from django.urls import reverse, resolve
from django.views.generic import ListView, DetailView, FormView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db import transaction


from courses.models import (
    Course,
    Page,
    Question,
    Variant,
    CourseEnrollment,
    Result,
    course_cover_path,
)

from courses.forms import (
    CourseForm,
    PageForm,
    QuestionForm,
    VariantForm,
)

from accounts.models import Account

START_PAGE_NUMBER = 1
logger = logging.getLogger('eLearning')


@method_decorator(login_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    context_object_name = 'course_list'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{request.user} viewed course list.')
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
    course_pk = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        try:
            self.course_instance = Course.objects.get(pk=self.course_pk)
        except Course.DoesNotExist:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if self.course_instance.owner_user != request.user:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
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
            logger.info(f'{request.user} updated course - {self.course_pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update course - {self.course_pk}.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_pk'] = self.course_pk
        kwargs['course_types'] = self.model.COURSE_USER_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        kwargs['type'] = self.course_instance.type
        kwargs['status'] = self.course_instance.status
        # kwargs['action_url'] = 'course_edit'   # 'course_edit course_pk'# + str(self.course_pk)
        # kwargs['action_url'] = reverse('course_edit', args=[self.course_pk])
        # kwargs['action_url'] = resolve(f'courses/{self.course_pk}/')
        # print(kwargs['action_url'])
        kwargs['page_list'] = self.course_instance.page_set.all()
        kwargs['view'] = 'edit'
        kwargs['cover_url'] = self.course_instance.cover.url
        return kwargs

    def form_valid(self, form):
        # TODO: remove old cover
        # TODO: revise bound and unboubd forms
        # TODO: save thumbnail
        form.initial = {
            "name": self.request.POST.get("name"),
            "min_pass_grade": self.request.POST.get("min_pass_grade"),
            "type": self.request.POST.get("type"),
            "status": self.request.POST.get("status"),
            "content": self.request.POST.get("content"),
            "cover": self.request.FILES.get("cover"),
        }
        course = form.save()
        return render(self.request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class  CreateCourseView(FormView):
    template_name = "courses/course_edit.html"
    form_class = CourseForm
    model = Course
    course_pk = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            logger.info(f'{request.user} created course - {self.course_pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't created course - {self.course_pk}.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_types'] = self.model.COURSE_USER_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        # kwargs['action_url'] = 'course_create'
        kwargs['view'] = 'create'
        return kwargs

    def form_valid(self, form):
        form.instance.owner_type = 'usr'
        form.instance.owner_user = self.request.user
        course = form.save()
        Page.objects.create(
            course=course,
            content="",
            number=START_PAGE_NUMBER,
        )
        self.course_pk = course.pk
        success_url = reverse('course_edit', kwargs={'course_pk': self.course_pk})
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


@method_decorator(login_required, name='dispatch')
class  CreatePageView(FormView):
    template_name = "courses/page_edit.html"
    form_class = PageForm
    model = Page
    course_instance = None
    course_pk = None
    page_pk = None
    page_number = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        self.course_instance = Course.objects.get(pk=self.course_pk)
        self.page_number = Page.objects.filter(course=self.course_instance).count() + 1
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['view'] = 'create'
        kwargs['course_pk'] = self.course_pk
        kwargs['page_number'] = self.page_number
        return kwargs

    def form_valid(self, form):
        form.instance.course = self.course_instance
        page = form.save()
        self.page_pk = page.pk
        logger.info(f'{self.request.user} created page - {self.page_pk}.')
        success_url = reverse('page_edit', kwargs={'course_pk': self.course_pk, 'page_pk': self.page_pk})
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        logger.info(f"{self.request.user} didn't created page.")
        form.initial = {
            "number": self.request.POST.get("number"),
            "content": self.request.POST.get("content"),
        }
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required, name='dispatch')
class EditPageView(FormView):
    template_name = "courses/page_edit.html"
    form_class = PageForm
    model = Page
    extra_context = {"success_message": ""}
    page_instance = None
    course_pk = None
    page_pk = None

    def dispatch(self, request, *args, **kwargs):
        self.page_pk = kwargs['page_pk']
        self.course_pk = kwargs['course_pk']
        try:
            self.course_instance = Course.objects.get(pk=self.course_pk)
            self.page_instance = Page.objects.get(pk=self.page_pk)
        except (Course.DoesNotExist, Page.DoesNotExist):
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if self.course_instance.owner_user != request.user or self.page_instance.course != self.course_instance:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.page_instance})
        return kwargs

    def get_initial(self):
        self.initial = {
            "number": self.page_instance.number,
            "content": self.page_instance.content,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.extra_context["success_message"] = "Page updated"
            logger.info(f'{request.user} updated page - {self.page_pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update page - {self.page_pk}.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['page_pk'] = self.page_pk
        kwargs['course_pk'] = self.course_pk
        kwargs['view'] = 'edit'
        kwargs['question_list'] = self.page_instance.question_set.all()
        kwargs['question_types'] = dict(Question.QUESTION_TYPE_CHOICES)
        return kwargs

    def form_valid(self, form):
        form.initial = {
            "content": self.request.POST.get("content"),
        }
        form.save()
        return render(self.request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class  CreateQuestionView(FormView):
    template_name = "courses/question_edit.html"
    form_class = QuestionForm
    model = Question
    course_pk = None
    page_pk = None
    question_pk = None
    page_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        self.page_pk = kwargs['page_pk']
        self.page_instance = Page.objects.get(pk=self.page_pk)
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['view'] = 'create'
        kwargs['course_pk'] = self.course_pk
        kwargs['page_pk'] = self.page_pk
        kwargs['question_types'] = self.model.QUESTION_TYPE_CHOICES
        return kwargs

    def form_valid(self, form):
        form.instance.page = self.page_instance
        question = form.save()
        Variant.objects.create(
            question=question,
            content="",
            is_correct=False,
        )
        self.question_pk = question.pk
        logger.info(f'{self.request.user} created question - {self.question_pk}.')
        success_url = reverse('question_edit', kwargs={
            'course_pk': self.course_pk,
            'page_pk': self.page_pk,
            'question_pk': self.question_pk
            })
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        logger.info(f"{self.request.user} didn't create question.")
        form.initial = {
            "type": self.request.POST.get("type"),
            "content": self.request.POST.get("content"),
        }
        return self.render_to_response(self.get_context_data(form=form))


# TODO: transfer js code in static file
@method_decorator(login_required, name='dispatch')
class EditQuestionView(FormView):
    template_name = "courses/question_edit.html"
    form_class = QuestionForm
    model = Question
    extra_context = {"success_message": ""}
    course_pk = None
    page_pk = None
    question_pk = None
    question_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        self.page_pk = kwargs['page_pk']
        self.question_pk = kwargs['question_pk']
        try:
            self.course_instance = Course.objects.get(pk=self.course_pk)
            self.page_instance = Page.objects.get(pk=self.page_pk)
            self.question_instance = Question.objects.get(pk=self.question_pk)
        except (Course.DoesNotExist, Page.DoesNotExist, Question.DoesNotExist):
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if (self.course_instance.owner_user != request.user 
                or self.page_instance.course != self.course_instance
                or self.question_instance.page != self.page_instance):
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)

        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.question_instance})
        return kwargs

    def get_initial(self):
        self.initial = {
            "type": self.question_instance.type,
            "content": self.question_instance.content,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.extra_context["success_message"] = "Question updated"
            logger.info(f'{request.user} updated question - {self.question_pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update question - {self.question_pk}.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_pk'] = self.course_pk
        kwargs['page_pk'] = self.page_pk
        kwargs['question_pk'] = self.question_pk
        kwargs['question_types'] = self.model.QUESTION_TYPE_CHOICES
        kwargs['type'] = self.question_instance.type
        kwargs['view'] = 'edit'
        kwargs['variant_list'] = self.question_instance.variant_set.all()
        return kwargs

    def form_valid(self, form):
        form.initial = {
            "type": self.request.POST.get("type"),
            "content": self.request.POST.get("content"),
        }
        form.save()
        return render(self.request, self.template_name, self.get_context_data())

@method_decorator(login_required, name='dispatch')
class  CreateVariantView(FormView):
    template_name = "courses/variant_edit.html"
    form_class = VariantForm
    model = Variant
    course_pk = None
    page_pk = None
    question_pk = None
    variant_pk = None
    question_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        self.page_pk = kwargs['page_pk']
        self.question_pk = kwargs['question_pk']
        self.question_instance = Question.objects.get(pk=self.question_pk)
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['view'] = 'create'
        kwargs['course_pk'] = self.course_pk
        kwargs['page_pk'] = self.page_pk
        kwargs['question_pk'] = self.question_pk
        return kwargs

    def form_valid(self, form):
        form.instance.question = self.question_instance
        variant = form.save()
        self.variant_pk = variant.pk
        logger.info(f'{self.request.user} created variant - {self.variant_pk}.')
        success_url = reverse('variant_edit', kwargs={
            'course_pk': self.course_pk,
            'page_pk': self.page_pk,
            'question_pk': self.question_pk,
            'variant_pk': self.variant_pk,
            })
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        logger.info(f"{self.request.user} didn't create variant.")
        form.initial = {
            "is_correct": self.request.POST.get("is_correct"),
            "content": self.request.POST.get("content"),
        }
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        content = form['content'].value()
        try:
            Variant.objects.get(
                question=self.question_instance,
                content=content,
            )
        except Variant.DoesNotExist:
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            form.add_error(None, f'A variant with "{content}" content already exists.')
            return self.form_invalid(form)

# TODO: transfer js code in static file
# TODO: add question type check
@method_decorator(login_required, name='dispatch')
class EditVariantView(FormView):
    template_name = "courses/variant_edit.html"
    form_class = VariantForm
    model = Variant
    extra_context = {"success_message": ""}
    course_pk = None
    page_pk = None
    question_pk = None
    variant_pk = None
    variant_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.course_pk = kwargs['course_pk']
        self.page_pk = kwargs['page_pk']
        self.question_pk = kwargs['question_pk']
        self.variant_pk = kwargs['variant_pk']
        self.variant_instance = Variant.objects.get(pk=self.variant_pk)
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.variant_instance})
        return kwargs

    def get_initial(self):
        self.initial = {
            "is_correct": self.variant_instance.is_correct,
            "content": self.variant_instance.content,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        question_instance = Question.objects.get(pk=self.question_pk)
        content = form['content'].value()
        try:
            Variant.objects.get(
                question=question_instance,
                content=content,
            )
        except Variant.DoesNotExist:
            if form.is_valid():
                self.extra_context["success_message"] = "Variant updated"
                logger.info(f'{request.user} updated variant - {self.variant_pk}.')
                return self.form_valid(form)
            else:
                logger.info(f"{request.user} didn't update variant - {self.variant_pk}.")
                return self.form_invalid(form)
        else:
            form.add_error(None, f'A variant with "{content}" content already exists.')
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_pk'] = self.course_pk
        kwargs['page_pk'] = self.page_pk
        kwargs['question_pk'] = self.question_pk
        kwargs['variant_pk'] = self.variant_pk
        kwargs['is_correct'] = self.variant_instance.is_correct
        kwargs['view'] = 'edit'
        return kwargs

    def form_valid(self, form):
        form.initial = {
            "is_correct": self.request.POST.get("is_correct"),
            "content": self.request.POST.get("content"),
        }
        form.save()
        return render(self.request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'
    course_pk = None

    def get_object(self):
        self.course_pk = self.kwargs.get('course_pk')
        return get_object_or_404(Course, id=self.course_pk)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        try:
            CourseEnrollment.objects.get(user=request.user, course=self.object)
        except CourseEnrollment.DoesNotExist:
            return self.render_to_response(context)
        else:
            redirect_url = reverse('course_welcom', kwargs={
            'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_pk'] = self.course_pk
        kwargs['is_fav'] = "False"
        for fav_course in self.request.user.favorite_courses.all():
            if fav_course == self.object:
                kwargs['is_fav'] = "True"
                break
        return kwargs


@method_decorator(login_required, name='dispatch')
class CourseWelcomView(View):
    model = CourseEnrollment
    context_object_name = 'course_enrollment'
    template = 'courses/course_welcom.html'
    course_enrollment_instance = None
    course_pk = None
    course_instance = None
    user = None

    def get(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.user = request.user
        self.course_instance = Course.objects.get(pk=self.course_pk)
        try:
            self.course_enrollment_instance = CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
        except CourseEnrollment.DoesNotExist:
            redirect_url = reverse('course_detail', kwargs={
            'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
        else:
            context = self.get_context_data(self.course_enrollment_instance)
            return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.user = request.user
        self.course_instance = Course.objects.get(pk=self.course_pk)
        page = Page.objects.filter(course=self.course_instance).get(number=START_PAGE_NUMBER)
        try:
            CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
        except CourseEnrollment.DoesNotExist:
            CourseEnrollment.objects.create(
                user=self.user,
                course=self.course_instance,
                current_page=page,
                points=None,
            )
        redirect_url = reverse('course_welcom', kwargs={
        'course_pk': self.course_pk,
        })
        return HttpResponseRedirect(redirect_url)
    
    def get_context_data(self, object_):
        current_page = self.course_enrollment_instance.current_page
        if not current_page:
            current_page = self.course_enrollment_instance.course.page_set.get(number=START_PAGE_NUMBER)
        
        course_pages = self.course_enrollment_instance.course.page_set.all()
        total_points = 0.0
        for page in course_pages:
            total_points += Question.objects.filter(page=page).count()

        is_fav = "False"
        for fav_course in self.request.user.favorite_courses.all():
            if fav_course == self.course_instance:
                is_fav = "True"
                break

        context = {
            self.context_object_name: object_,
            'page_list': course_pages,
            'current_page': current_page,
            'total_points': total_points,
            'grade': self.course_enrollment_instance.grade,
            'total_grade': Course.TOTAL_GRADE,
            "is_fav": is_fav,
        }
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(transaction.atomic, name='post')
class CoursePageView(View):
    model = Page
    context_object_name = 'current_page'
    with_input_template = 'courses/course_page_with_input.html'
    without_input_template = 'courses/course_page_without_input.html'
    course_pk = None
    course_instance = None
    page_pk = None
    page_instance = None
    user = None

    def get(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.course_instance = Course.objects.get(pk=self.course_pk)
        self.page_pk = self.kwargs.get('page_pk')
        self.page_instance = Page.objects.get(pk=self.page_pk)
        self.user = self.request.user
        self.course_enrollment = None
        self.is_course_enrollment_finished = None

        try:
            self.course_enrollment = CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
            self.is_course_enrollment_finished = True if self.course_enrollment.finished_at else False
        except CourseEnrollment.DoesNotExist:
            redirect_url = reverse('course_detail', kwargs={
                'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
        else:
            # unallowed page, redirect to current page
            if self.page_instance.number > self.course_enrollment.current_page.number:
                redirect_url = reverse('course_page', kwargs={
                    'course_pk': self.course_pk,
                    'page_pk': self.course_enrollment.current_page.pk,
                })
                return HttpResponseRedirect(redirect_url)

            # there are no questions
            if not self.page_instance.question_set.all():
                # ------ check page type - (last or next) ------
                current_page_number = self.page_instance.number
                next_page_number = current_page_number + 1
                try:
                    next_page = Page.objects.get(course=self.course_instance, number=next_page_number)
                # last page
                except Page.DoesNotExist:
                    if not self.course_enrollment.finished_at:
                        self.finish_course_enrollment()
                    button_type='Finish'
                    next_page_pk = None
                # next page
                else:
                    if self.course_enrollment.current_page.number == current_page_number and not self.course_enrollment.finished_at:
                        self.update_course_enrollment(next_page)
                    button_type = 'Next'
                    next_page_pk = next_page.pk

                context = self.get_context_data(
                    object_=self.page_instance,
                    button_type=button_type,
                    next_page_pk=next_page_pk,
                    finished=self.is_course_enrollment_finished,
                )
                return render(request, self.without_input_template, context)

            # there are questions
            else:
                results = Result.objects.filter(page=self.page_instance, user=self.user)
                # questions was passed, show template without input
                if results:

                    # ------ get tasks and user answers(all and correct) ------
                    tasks = self.get_tasks()
                    user_variants = self.get_user_variants(results)
                    correct_user_questions = self.get_correct_user_questions(results)
                    incorrect_user_questions = self.get_incorrect_user_questions(results)

                    # ------ check page type - (last or next) ------
                    current_page_number = self.page_instance.number
                    next_page_number = current_page_number + 1
                    try:
                        next_page = Page.objects.get(course=self.course_instance, number=next_page_number)
                    # last page
                    except Page.DoesNotExist:
                        if not self.course_enrollment.finished_at:
                            self.finish_course_enrollment()
                        button_type='Finish'
                        next_page_pk = None
                    # next page
                    else:
                        if self.course_enrollment.current_page.number == current_page_number and not self.course_enrollment.finished_at:
                            self.update_course_enrollment(next_page)
                        button_type = 'Next'
                        next_page_pk = next_page.pk
                    
                    variant_ids = CoursePageView.convert_variants_to_ids(user_variants)
                    correct_questions_ids = CoursePageView.convert_questions_to_ids(correct_user_questions)
                    incorrect_questions_ids = CoursePageView.convert_questions_to_ids(incorrect_user_questions)
                    context = self.get_context_data(
                        object_=self.page_instance,
                        button_type=button_type,
                        next_page_pk=next_page_pk,
                        tasks=tasks,
                        user_variants=variant_ids,
                        correct_questions=correct_questions_ids,
                        incorrect_questions=incorrect_questions_ids,
                        finished=self.is_course_enrollment_finished,
                    )
                    return render(request, self.without_input_template, context)
                # questions wasn't passed, show template with input
                else:
                    tasks = self.get_tasks()
                    # current_page_number = self.page_instance.number
                    # next_page_number = current_page_number + 1
                    # try:
                    #     next_page = Page.objects.get(course=self.course_instance, number=next_page_number)
                    # # last page
                    # except Page.DoesNotExist:
                    #     next_page_pk = None
                    # # next page
                    # else:
                        # next_page_pk = next_page.pk

                    question_types = dict(Question.QUESTION_TYPE_CHOICES)
                    context = self.get_context_data(
                        object_=self.page_instance,
                        # next_page_pk=next_page_pk,
                        tasks=tasks,
                        finished=self.is_course_enrollment_finished,
                        question_types=question_types,
                    )
                    return render(request, self.with_input_template, context)

    def post(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.course_instance = Course.objects.get(pk=self.course_pk)
        self.page_pk = self.kwargs.get('page_pk')
        self.page_instance = Page.objects.get(pk=self.page_pk)
        self.user = self.request.user
        self.course_enrollment = None
        # self.is_course_enrollment_finished = None
        try:
            self.course_enrollment = CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
            # self.is_course_enrollment_finished = True if self.course_enrollment.finished_at else False
        except CourseEnrollment.DoesNotExist:
            redirect_url = reverse('course_detail', kwargs={
            'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
        else:
            results = Result.objects.filter(page=self.page_instance, user=self.user)
            if not results:
                # ------ save user input ------
                user_input = json.loads(request.body.decode('utf-8'))

                # iterate by each question and add Result to DB
                for question_pk, variant_pks in user_input.items():
                    try:
                        question_pk = int(question_pk)
                        variant_pks = list(map(lambda x : int(x), variant_pks))
                    except ValueError:
                        # TODO: what should I do?
                        status = False
                        raise ValueError("Exeption was accur during post invalid data to CoursePageView. It shouldn't happend.")
                    question = Question.objects.get(pk=question_pk)

                    # correct variants
                    # using dict for future comparation
                    correct_variants = {}
                    for variant in question.variant_set.all():
                        if variant.is_correct:
                            correct_variants[variant.pk] = variant

                    # users variants
                    # using dict for future comparation
                    user_variants = {}
                    for variant_pk in variant_pks:
                        variant = Variant.objects.get(pk=variant_pk)
                        user_variants[variant.pk] = variant

                    is_correct = True if user_variants == correct_variants else False

                    user_variant_pks = user_variants.keys()
                    user_variant_pks = list(map(lambda x : str(x), user_variant_pks))
                    user_variant_pks = Result.RESULTS_SEPARATOR.join(user_variant_pks)

                    Result.objects.create(
                        user=self.user,
                        question=question,
                        results=user_variant_pks,
                        is_correct=is_correct,
                        page=self.page_instance,
                    )

                # calculate points
                points = self.course_enrollment.points
                results = Result.objects.filter(page=self.page_instance, user=self.user)
                correct_user_questions = self.get_correct_user_questions(results)
                earned_points = len(correct_user_questions)
                if points:
                    self.course_enrollment.points += earned_points
                else:
                    self.course_enrollment.points = earned_points
                if earned_points != 0:
                    self.course_enrollment.save()
                print("first time")
                return JsonResponse({
                    "view_status": True,
                    "data_saved": True,
                })
            else:
                print("second time")
                return JsonResponse({
                    "view_status": True,
                    "data_saved": False,
                })

    def get_tasks(self):
        questions = self.page_instance.question_set.all()
        tasks = []
        for question in questions:
            tasks.append({
                'question': question,
                'variants': question.variant_set.all(),
            })
        return tasks

    def get_user_variants(self, results):
        user_variant = []
        for result in results:
            if result.results:
                variant_pks = result.results.split(Result.RESULTS_SEPARATOR)
                for variant_pk in variant_pks:
                    user_variant.append(
                        Variant.objects.get(pk=variant_pk)
                    )
        return user_variant

    @staticmethod
    def convert_variants_to_ids(variants):
        ids = []
        for variant in variants:
            ids.append(f"v_{variant.pk}")
        return Result.RESULTS_SEPARATOR.join(ids)

    @staticmethod
    def convert_questions_to_ids(questions):
        ids = []
        for question in questions:
            ids.append(f"q_{question.pk}")
        return Result.RESULTS_SEPARATOR.join(ids)
    
    def get_correct_user_questions(self, results):
        correct_user_questions = []
        for result in results:
            if result.is_correct:
                correct_user_questions.append(
                    Question.objects.get(pk=result.question.pk)
                )
        return correct_user_questions

    def get_incorrect_user_questions(self, results):
        incorrect_user_questions = []
        for result in results:
            if not result.is_correct:
                incorrect_user_questions.append(
                    Question.objects.get(pk=result.question.pk)
                )
        return incorrect_user_questions

    def finish_course_enrollment(self):
        self.course_enrollment.finished_at = date.today()
        self.course_enrollment.is_active = False

        # count questions
        questions = 0
        for page in self.course_enrollment.course.page_set.all():
            if page.question_set.count() != 0:
                questions += 1
                break
        # course without questions will be passed automaticaly
        if not questions:
            self.course_enrollment.is_pass = True
        # if course have questions then user will pass course enrollmnt if his grade => minimal pass grade
        else:
            if self.course_enrollment.grade >= self.course_enrollment.course.min_pass_grade:
                self.course_enrollment.is_pass = True
        self.course_enrollment.progress = 100
        self.course_enrollment.save()

    def update_course_enrollment(self, next_page):
        self.course_enrollment.current_page = next_page
        total_page_count = Page.objects.filter(course=self.course_instance).count()
        self.course_enrollment.progress = self.page_instance.number / total_page_count * 100
        self.course_enrollment.save()

    def get_context_data(self, object_=None, **kwargs):
        context = kwargs
        context[self.context_object_name] = object_
        context['course_pk'] = self.course_pk
        context['page_pk'] = self.page_pk
        return context


def course_rate(request, course_pk):
    if request.method == 'POST':
        body = json.loads(request.body)
        course_pk = body['course_pk']
        course = Course.objects.get(pk=course_pk)
        user_email = body['user']
        user = Account.objects.get(email=user_email)
        rate = body['rate']
        try:
            course_enrollment = CourseEnrollment.objects.get(
                course=course,
                user=user,
            )
        except CourseEnrollment.DoesNotExist:
            logger.info("Rate ajax wasn't success.")
            return HttpResponse("Invalid request.")
        else:
            logger.info("Rate ajax was success.")
            course_enrollment.rate = rate
            course_enrollment.save()

            # recalculate course rating
            rating = 0.0
            rating_amount = 0
            course_enrollments = CourseEnrollment.objects.filter(course=course).all()
            for course_enrollment in course_enrollments:
                rate = course_enrollment.rate
                if rate:
                    rating_amount += 1
                    rating += rate
            try:
                rating = rating / rating_amount
            except ZeroDivisionError:
                rating = 0.0

            course.rating = rating
            course.save()

            return HttpResponse("Success!")


def course_add_favorite(request, course_pk):
    if request.method == 'POST':
        user = request.user
        try:
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            logger.info("Request statistics for not existing course.")
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        else:
            body = json.loads(request.body)
            status = body['is_pressed']
            print(status)
            if status:
                user.favorite_courses.add(course)
            else:
                user.favorite_courses.remove(course)
            return JsonResponse({
                    "view_status": True,
                    "data_saved": True,
                })


@login_required
def course_statistics_view(request, course_pk):
    if request.method == "GET":
        try:
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            logger.info("Request statistics for not existing course.")
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        else:
            if not request.user == course.owner_user:
                logger.info("User requested statistics not for his course.")
                redirect_url = reverse('home', kwargs={})
                return HttpResponseRedirect(redirect_url)
            else:
                finished_enrollments = CourseEnrollment.objects.filter(course=course, finished_at__isnull=False)
                failed = 0
                success = 0
                for finished_enrollment in finished_enrollments:
                    if finished_enrollment.is_pass:
                        success += 1
                    else:
                        failed += 1
                students = CourseEnrollment.objects.filter(course=course, finished_at__isnull=True).count()

                course_enrollments = CourseEnrollment.objects.filter(course=course).all()
                rating = [0, 0, 0, 0, 0]
                for course_enrollment in course_enrollments:
                    if course_enrollment.rate:
                        rating[int(course_enrollment.rate) - 1] += 1

                students_amount = CourseEnrollment.objects.filter(course=course).count()
                context = {
                    'failed': failed,
                    'success': success,
                    'students': students,
                    'rating': rating,
                    'students_amount': students_amount,
                    'average_rating': course.rating,
                }
                return render(request, 'courses/statistics.html', context)
