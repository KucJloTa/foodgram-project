from django import forms
from django.forms import CheckboxSelectMultiple

from .models import Recipe


class RecipeForm(forms.ModelForm):

    amount = forms.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'title',
            'breakfast',
            'lunch',
            'dinner',
            'image',
            'description',
            'cooking_time']
        widgets = {
            'tag': CheckboxSelectMultiple(),
        }
