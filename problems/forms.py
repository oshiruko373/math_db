# problems/forms.py
from django import forms
from .models import Problem, ThoughtProcess, Tag
from django_select2.forms import Select2MultipleWidget

class ProblemForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget,  # Select2ウィジェットを利用
        required=False,
    )

    class Meta:
        model = Problem
        fields = [
            'source_year',
            'source_university',
            'source_faculty',
            'boxURL',
            'difficulty',
            'tags',
            'thought_processes',
            'good_points',  # `良い点`
            'usage_location',  # `扱う場所`
        ]
        widgets = {
            'thought_processes': forms.CheckboxSelectMultiple(),
        }

class ThoughtProcessForm(forms.ModelForm):
    problems = forms.ModelMultipleChoiceField(
        queryset=Problem.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label="Related Problems",
    )

    class Meta:
        model = ThoughtProcess
        fields = ['process', 'related_processes']
        widgets = {
            'related_processes': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 編集対象の思考プロセス自身を related_processes の選択肢から除外
            self.fields['related_processes'].queryset = ThoughtProcess.objects.exclude(pk=self.instance.pk)



