from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("text",)


class ComparisonForm(forms.Form):
    """
    Форма для checkbox в сервисе сравнения
    """

    flag = forms.BooleanField()
