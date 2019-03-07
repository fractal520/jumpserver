# ~*~ coding: utf-8 ~*~

from django import forms
from .models import *


class TaskForm(forms.ModelForm):
    class Meta:
        model = PlayBookTask
        fields = [
            'name', 'desc', 'ansible_role', 'run_as_admin', 'run_as', 'extra_vars'
        ]
        help_texts = {

        }
        widgets = {
            'desc': forms.Textarea(),
        }
