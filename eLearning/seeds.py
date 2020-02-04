from faker import Faker
import random

from django.db import transaction

fake=Faker()

course_name_words = [
    'Accounting and Business',
    'Accounting and Finance',
    'Bachelor of Business and Laws BBL (Cornwall)',
    'Biochemistry',
    'Classical Studies and Modern Languages',
    'Classical Studies and Philosophy',
    'Economics',
    'Economics and Finance',
    'Economics and Politics',
    'Economics with Econometrics',
    'Electronic Engineering',
    'Geography',
    'Human Sciences',
    'Sociology',
]

from courses.models import (
    Course,
    Page,
    Question,
    Variant,
)

from accounts.models import (
    Account,
)

@transaction.atomic
def seed_courses():
    accounts = Account.objects.all()
    for _ in list(range(0, 14)):
        course_name = random.choice(course_name_words)
        course_name_words.remove(course_name)
        Course.objects.create(
            owner_type="usr",
            owner_user=random.choice(accounts),
            min_pass_grade=6,
            status='rdy',
            type='pbl',
            content=fake.text(),
            name=course_name,
        )

@transaction.atomic
def seed_page(course):
    for i in list(range(0, 6)):
        Page.objects.create(
            number=i + 1,
            content=fake.text(),
            course=course,
        )

def get_question_types():
    types = [type[0] for type in Question.QUESTION_TYPE_CHOICES]
    return types

@transaction.atomic
def seed_question(page):
    types = get_question_types()
    for i in list(range(0, 6)):
        type = random.choice(types)
        Question.objects.create(
            type=type,
            content=fake.text(),
            page=page,
        )


@transaction.atomic
def seed_variant(question):
    variants = []
    for _ in list(range(0, 3)):
        variants.append(Variant.objects.create(
            question=question,
            content=fake.text(),
            is_correct=False,
        ))
    if question.type == 'chb':
        correct_variants = random.choices(variants, k=2)
    elif question.type == 'rad':
        correct_variants = [random.choice(variants)]

    for variant in correct_variants:
        variant.is_correct = True
        content = variant.content
        variant.content = "True " + content
        variant.save()


# ------------ seed courses ------------
seed_courses()


# ------------ seed pages ------------
courses = Course.objects.all()
for course in courses:
    seed_page(course)


# ------------ seed questions ------------
pages = Page.objects.all()
pages_amount = pages.count() // 3
pages = random.choices(pages, k=pages_amount)
for page in pages:
    seed_question(page)


# ------------ seed variants ------------
questions = Question.objects.all()
variants = Variant.objects.all()
for question in questions:
    seed_variant(question)
print("done")