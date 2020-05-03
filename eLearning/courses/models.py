import logging
import os
import math

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from accounts.models import Account

logger = logging.getLogger('eLearning')

def validate_image_size(img):
        img_size = img.file.size
        print(img_size)
        if img_size > Course.MAX_IMAGE_SIZE:
            raise ValidationError(f"Max image size is {Course.MB} MB.")


def course_cover_path(course, filename):
    return f'courses/{filename}'


class Course(models.Model):
    COURSE_STATUS_CHOICES = [
        ('drf', 'draft'),
        ('rdy', 'ready'),
    ]
    # all choices
    COURSE_TYPE_CHOICES = [
        ('pbl', 'public'),
        ('prv', 'private'),
        ('ind', 'individual'),
    ]
    COURSE_USER_TYPE_CHOICES = [
        ('pbl', 'public'),
        ('ind', 'individual'),
    ]
    COURSE_ORG_TYPE_CHOICES = [
        ('pbl', 'public'),
        ('prv', 'private'),
        ('ind', 'individual'),
    ]
    COURSE_OWNER_TYPE_CHOICES = [
        ('usr', 'user'),
    ]
    MB = 2 ** 20
    MAX_IMAGE_SIZE = 5 * MB
    DEFAULT_COURSE_COVER = 'courses/default.png'
    TOTAL_GRADE = 10

    owner_type = models.CharField(max_length=3, choices=COURSE_OWNER_TYPE_CHOICES,)
    owner_user = models.ForeignKey(
        Account, null=True, on_delete=models.CASCADE, related_name='managed_courses'
    )
    min_pass_grade = models.FloatField(verbose_name='minimum pass grade')
    status = models.CharField(
        max_length=3, choices=COURSE_STATUS_CHOICES, default='drf',
    )
    type = models.CharField(max_length=3, choices=COURSE_TYPE_CHOICES, default='pbl')
    content = models.TextField()
    name = models.CharField(max_length=255)
    rating = models.FloatField(null=True)
    students = models.ManyToManyField(Account, related_name='individual_courses')
    cover = models.ImageField(upload_to=course_cover_path, default=DEFAULT_COURSE_COVER,
                              validators=[validate_image_size])


class CertificateTemplate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


class Page(models.Model):
    number = models.IntegerField()
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('chb', 'checkbox'),
        ('rad', 'radio'),
    ]
    type = models.CharField(max_length=3, choices=QUESTION_TYPE_CHOICES)
    content = models.TextField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE)


class Variant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    is_correct = models.BooleanField()


class Certificate(models.Model):
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE)
    content = models.TextField()


class CourseEnrollment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, null=True)
    current_page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    started_at = models.DateField(auto_now_add=True)
    finished_at = models.DateField(null=True)
    points = models.FloatField(null=True)
    progress = models.FloatField(null=True)
    rate = models.FloatField(null=True)
    is_active = models.BooleanField(default=True)
    is_pass = models.BooleanField(default=False)
    _grade = models.IntegerField(db_column='grade', null=True)

    @property
    def grade(self):
        course_pages = self.course.page_set.all()
        total_points = 0.0
        for page in course_pages:
            total_points += Question.objects.filter(page=page).count()
        if self.points:
            grade = math.ceil(self.points * Course.TOTAL_GRADE / total_points)
        else:
            grade = None
        return grade


class Result(models.Model):
    RESULTS_SEPARATOR = ' '
    results = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
