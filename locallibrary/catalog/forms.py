import datetime

from django import forms
from django.forms import ModelForm
from catalog.models import BookInstance

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class DateValidationMixin:
    def validate_date(self, date):
        if date < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        if date > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        
class RenewBookForm(forms.Form, DateValidationMixin):
    renewal_date = forms.DateField(help_text=_("Enter a date between now and 4 weeks (default 3)."))

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        self.validate_date(data)
        return data

class RenewBookModelForm(ModelForm, DateValidationMixin):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        self.validate_date(data)
        return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}
