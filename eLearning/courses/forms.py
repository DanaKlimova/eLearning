from django import forms

from courses.models import (
    Course,
    Page,
    Question,
    Variant,
)


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


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (
            'number',
            'content',
        )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            'type',
            'content',
        )


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = (
            'is_correct',
            'content',
        )

class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])


class CheckboxQuestionForm(forms.Form):
    question_pk = forms.IntegerField()
    content = forms.CharField(label='Question')
    choices = DynamicMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=[],
        label='Variants'
    )


class RadioQuestionForm(forms.Form):
    question_pk = forms.IntegerField()
    content = forms.CharField(label='Question')
    choices = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=[],
        label='Variants',
    )
