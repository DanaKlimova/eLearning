from django import forms

from courses.models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'min_pass_grade',
            'status',
            'type',
            'content',
            'name',
            # 'students',
        )
