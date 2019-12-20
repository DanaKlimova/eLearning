import logging

from django.db import models

from accounts.models import Account

logger = logging.getLogger('eLearning')


class Course(models.Model):
    COURSE_STATUS_CHOICES = [
        ('drf', 'draft'),
        ('rdy', 'ready'),
    ]
    COURSE_TYPE_CHOICES = [
        ('pbl', 'public'),
        ('prv', 'private'),
        ('ind', 'individual'),
    ]
    COURSE_OWNER_TYPE_CHOICES = [
        ('usr', 'user'),
    ]

    owner_type = models.CharField(max_length=3, choices=COURSE_OWNER_TYPE_CHOICES,)
    owner_user = models.ForeignKey(
        Account, null=True, on_delete=models.CASCADE, related_name='owner_user'
    )
    min_pass_grade = models.FloatField(verbose_name='minimum pass grade')
    status = models.CharField(
        max_length=3, choices=COURSE_STATUS_CHOICES, default='drf',
    )
    type = models.CharField(max_length=3, choices=COURSE_TYPE_CHOICES, default='pbl')
    content = models.TextField()
    name = models.CharField(max_length=255)
    rating = models.FloatField()
    students = models.ManyToManyField(Account, related_name='students')


class CertificateTemplate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


class Page(models.Model):
    number = models.IntegerField()
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('slc', 'select'),
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
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE)
    current_page = models.ForeignKey(Page, on_delete=models.CASCADE)
    started_at = models.DateField()
    finished_at = models.DateField()
    grade = models.FloatField()
    progress = models.FloatField()
    rate = models.FloatField()
    is_active = models.BooleanField()


class Results(models.Model):
    results = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
