from django import forms

from .models import Assignment


class AssignmentForm(forms.ModelForm):
    """Form to create or edit an assignment."""

    class Meta:
        model = Assignment

        fields = [
            "name",
            "due_date",
            "description",
            "module",
        ]

        widgets = {
            'due_date': forms.widgets.DateTimeInput(attrs={
                'type': 'datetime',
                'placeholder': 'dd/mm/yyyy hh:mm:ss',
            })
        }

