# forms.py
from django import forms
from django.contrib.admin import widgets
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _

from .models import Companies


class DatePicker(DateInput):

    input_type = "date"

    def format_value(self, value):
        return (
            value.isoformat()
            if value is not None and hasattr(value, "isoformat")
            else ""
        )


class CompaniesForm(forms.ModelForm):
    date_start = forms.DateField(widget=DatePicker(), label=_("Start date"))
    end_date = forms.DateField(widget=DatePicker(), label=_("End date"), required=False)

    class Meta:
        model = Companies
        fields = "__all__"
        exclude = ("export_date", "uuid")
