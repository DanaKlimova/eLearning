import logging
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.urls import reverse, resolve
from django.views.generic import ListView, DetailView, FormView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from courses.models import (
    Course,
    Page,
    Question,
    Variant,
    CourseEnrollment,
    Result,
)

from courses.forms import (
    CourseForm,
    PageForm,
    QuestionForm,
    VariantForm,
)


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
        self.course_instance = Course.objects.get(pk=self.course_pk)
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
        kwargs['course_types'] = self.model.COURSE_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        kwargs['type'] = self.course_instance.type
        kwargs['status'] = self.course_instance.status
        # kwargs['action_url'] = 'course_edit'   # 'course_edit course_pk'# + str(self.course_pk)
        # kwargs['action_url'] = reverse('course_edit', args=[self.course_pk])
        # kwargs['action_url'] = resolve(f'courses/{self.course_pk}/')
        # print(kwargs['action_url'])
        kwargs['page_list'] = self.course_instance.page_set.all()
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
        kwargs['course_types'] = self.model.COURSE_TYPE_CHOICES
        kwargs['course_statuses'] = self.model.COURSE_STATUS_CHOICES
        # kwargs['action_url'] = 'course_create'
        kwargs['view'] = 'create'
        return kwargs

    def form_valid(self, form):
        form.instance.owner_type = 'usr'
        form.instance.owner_user = self.request.user
        course = form.save()
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
        self.page_instance = Page.objects.get(pk=self.page_pk)
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
        self.question_instance = Question.objects.get(pk=self.question_pk)
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
        if form.is_valid():
            self.extra_context["success_message"] = "Variant updated"
            logger.info(f'{request.user} updated variant - {self.variant_pk}.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update variant - {self.variant_pk}.")
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
        # TODO: if there are no pages in course?
        page = Page.objects.filter(course=self.course_instance).get(number=1)
        try:
            CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
        except CourseEnrollment.DoesNotExist:
            CourseEnrollment.objects.create(
                user=self.user,
                course=self.course_instance,
                current_page=page,
                grade=None,
            )
        redirect_url = reverse('course_welcom', kwargs={
        'course_pk': self.course_pk,
        })
        return HttpResponseRedirect(redirect_url)
    
    def get_context_data(self, object_):
        current_page = self.course_enrollment_instance.current_page
        if not current_page:
            # TODO: is it magic number? Should I create constant for first page?
            # Constraint on page count of ready courses?
            current_page = self.course_enrollment_instance.course.page_set.get(number=1)
        
        course_pages = self.course_enrollment_instance.course.page_set.all()
        total_grade = 0.0
        for page in course_pages:
            total_grade += Question.objects.filter(page=page).count()
        context = {
            self.context_object_name: object_,
            'page_list': course_pages,
            'current_page': current_page,
            'total_grade': total_grade,
        }
        return context


@method_decorator(login_required, name='dispatch')
class CoursePageView(View):
    model = Page
    context_object_name = 'current_page'
    template = 'courses/course_page.html'
    course_pk = None
    course_instance = None
    page_pk = None
    page_instance = None
    user = None

    def get(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.page_pk = self.kwargs.get('page_pk')
        self.page_instance = Page.objects.get(pk=self.page_pk)
        self.user = self.request.user
        self.course_instance = Course.objects.get(pk=self.course_pk)
        try:
            course_enrollment = CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
        except CourseEnrollment.DoesNotExist:
            # TODO: create decorator for course enrollment existing?
            redirect_url = reverse('course_detail', kwargs={
            'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
        else:
            results = Result.objects.filter(page=self.page_instance, user=self.user)
            if results:
                current_page_number = course_enrollment.current_page.number
                next_page_number = current_page_number + 1
                try:
                    next_page = Page.objects.get(course=self.course_instance, number=next_page_number)
                # last page
                except Page.DoesNotExist:
                    button_type='Finish'
                    if course_enrollment.finished_at:
                        button_type='To course enrollment detail'
                    next_page_pk = None
                # next page
                else:
                    button_type = 'Next'
                    next_page_pk = next_page.pk

                tasks = self.get_tasks()

                users_answers = self.get_users_answers(results)
                correct_questions = self.get_correct_questions(results)

                context = self.get_context_data(
                    object_=self.page_instance,
                    tasks=tasks,
                    button_type=button_type,
                    users_answers=users_answers,
                    correct_questions=correct_questions,
                    task_type='text',
                )
            else:
                tasks = self.get_tasks()
                context = self.get_context_data(
                    object_=self.page_instance,
                    tasks=tasks,
                    button_type='Submit'
                )
            return render(request, self.template, context)

    def get_users_answers(self, results):
        users_answers = []
        for result in results:
            variants = result.results.split(Result.RESULTS_SEPARATOR)
            for variant in variants:
                users_answers.append(f'q_{result.question.pk}_v_{variant}')
        return Result.RESULTS_SEPARATOR.join(users_answers)

    def get_correct_questions(self, results):
        correct_questions = []
        for result in results:
            if result.is_correct:
                correct_questions.append(f'q_{result.question.pk}')
        return Result.RESULTS_SEPARATOR.join(correct_questions)

    @staticmethod
    def create_task(question):
        variants = [(variant.pk, variant.content) for variant in question.variant_set.all()]
        question_types = dict(Question.QUESTION_TYPE_CHOICES)
        task = {
            'question': question,
            'question_types': question_types,
            'variants': variants,
        }
        return task

    def get_tasks(self):
        questions = self.page_instance.question_set.all()
        tasks = []
        for question in questions:
            tasks.append(CoursePageView.create_task(question))
        return tasks

    def post(self, request, *args, **kwargs):
        self.course_pk = self.kwargs.get('course_pk')
        self.page_pk = self.kwargs.get('page_pk')
        self.page_instance = Page.objects.get(pk=self.page_pk)
        self.user = self.request.user
        self.course_instance = Course.objects.get(pk=self.course_pk)
        
        try:
            course_enrollment = CourseEnrollment.objects.get(user=self.user, course=self.course_instance)
        except CourseEnrollment.DoesNotExist:
            redirect_url = reverse('course_detail', kwargs={
            'course_pk': self.course_pk,
            })
            return HttpResponseRedirect(redirect_url)
        else:
            current_page_number = course_enrollment.current_page.number
            next_page_number = current_page_number + 1
            try:
                next_page = Page.objects.get(course=self.course_instance, number=next_page_number)
            # last page
            except Page.DoesNotExist:
                course_enrollment.finished_at = date.today()
                course_enrollment.is_active = False
                course_enrollment.progress = 100
                course_enrollment.save()
                button_type='Finish'
                next_page_pk = None
            # next page
            else:
                course_enrollment.current_page = next_page
                total_page_count = Page.objects.filter(course=self.course_instance).count()
                course_enrollment.progress = current_page_number / total_page_count * 100
                course_enrollment.save()
                button_type = 'Next'
                next_page_pk = next_page.pk

            user_input = dict(request.POST)
            del user_input['csrfmiddlewaretoken']

            correct_questions = []
            for question_pk, variants_content in user_input.items():
                question = Question.objects.get(pk=question_pk)
                # users variants
                users_variants = {}
                for variant_content in variants_content:
                    variant = Variant.objects.get(question=question, content=variant_content)
                    users_variants[variant.pk] = variant
                # correct variants
                correct_variants = {}
                for correct_variant in question.variant_set.all():
                    if correct_variant.is_correct:
                        correct_variants[correct_variant.pk] = correct_variant
                
                users_variant_pks = []
                for _, variant in users_variants.items():
                    users_variant_pks.append(str(variant.pk))

                is_correct = True if users_variants == correct_variants else False

                if is_correct:
                    correct_questions.append(f'q_{question.pk}')
                
                separator = Result.RESULTS_SEPARATOR
                users_variant_pks = separator.join(users_variant_pks)
                Result.objects.create(
                    user=self.user,
                    question=question,
                    results=users_variant_pks,
                    is_correct=is_correct,
                    page=self.page_instance,
                )

            tasks = self.get_tasks()
            grade = course_enrollment.grade
            if grade:
                course_enrollment.grade += len(correct_questions)
            else:
                course_enrollment.grade = len(correct_questions)
            course_enrollment.save()

            correct_questions = ' '.join(correct_questions)

            results = Result.objects.filter(page=self.page_instance, user=self.user)
            users_answers = self.get_users_answers(results)

            context = self.get_context_data(
                object_=self.page_instance,
                tasks=tasks,
                button_type=button_type,
                next_page_pk=next_page_pk,
                correct_questions=correct_questions,
                task_type='text',
                users_answers=users_answers,
            )
            return render(request, self.template, context) 

    def get_context_data(self, object_=None, **kwargs):
        context = kwargs
        context[self.context_object_name] = object_
        context['course_pk'] = self.course_pk
        context['page_pk'] = self.page_pk
        return context
