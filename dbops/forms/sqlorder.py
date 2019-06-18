import time
from django import forms
from django.utils.translation import gettext_lazy as _
from apps.common.utils import get_logger
from ..models.sqlinfo import SqlOrder
from ..lib.util import workid

logger = get_logger('jumpserver')

class SqlUpdateForm(forms.ModelForm):
    class Meta:
        model = SqlOrder
        fields = (
            'dbinfo', 'sql', 'type', 'backup', 'text'
        )

    widgets = {
        'dbinfo': forms.Select(attrs={
            'class': 'select2', 'data-placeholder': _('dbinfo')
        })
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.initial['type'] = 1
        self.initial['backup'] = 1

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.submit_user = self.user
        instance.work_id = workid()
#       instance.insert_date = time.localtime(time.time())

        if commit:
            instance.save()
        return instance
