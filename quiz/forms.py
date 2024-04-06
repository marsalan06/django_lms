from django import forms
from django.forms.widgets import RadioSelect, Textarea
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from django.forms.models import inlineformset_factory

from accounts.models import User
from .models import (
    Question,
    Quiz,
    MCQuestion,
    Choice,
    DescriptiveQuestion,
    DescriptiveAnswer,
)


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        # Check if the question has the `get_choices_list` method, assuming MCQs have this method.
        if hasattr(question, "get_choices_list"):
            choice_list = [x for x in question.get_choices_list()]
            self.fields["answers"] = forms.ChoiceField(
                choices=choice_list, widget=RadioSelect
            )
        elif hasattr(
            question, "sample_answer"
        ):  # Assuming descriptive questions have a 'sample_answer' attribute
            # For descriptive questions, provide a large text area for input.
            self.fields["answers"] = forms.CharField(
                widget=Textarea(attrs={"style": "width:100%", "rows": 5}),
                label="Your Answer",
                help_text="Write your answer here.",
            )


class EssayForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(EssayForm, self).__init__(*args, **kwargs)
        self.fields["answers"] = forms.CharField(
            widget=Textarea(attrs={"style": "width:100%"})
        )


class QuizAddForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(verbose_name=_("Questions"), is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super(QuizAddForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["questions"].initial = (
                self.instance.question_set.all().select_subclasses()
            )

    def save(self, commit=True):
        quiz = super(QuizAddForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data["questions"])
        self.save_m2m()
        return quiz


class MCQuestionForm(forms.ModelForm):
    class Meta:
        model = MCQuestion
        exclude = ()


MCQuestionFormSet = inlineformset_factory(
    MCQuestion,
    Choice,
    form=MCQuestionForm,
    fields=["choice", "correct"],
    can_delete=True,
    extra=5,
)


class DescriptiveQuestionForm(forms.ModelForm):
    class Meta:
        model = DescriptiveQuestion
        fields = ["content", "figure", "explanation", "sample_answer", "keywords"]
        widgets = {
            "content": Textarea(attrs={"cols": 80, "rows": 3}),
            "explanation": Textarea(attrs={"cols": 80, "rows": 3}),
            "sample_answer": Textarea(attrs={"cols": 80, "rows": 3}),
            "keywords": Textarea(attrs={"cols": 80, "rows": 2}),
        }


class DescriptiveAnswerForm(forms.ModelForm):
    class Meta:
        model = DescriptiveAnswer
        fields = ["question", "answer_text"]
