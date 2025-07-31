# forms.py
from django import forms
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
    date_end = forms.DateField(
        widget=DatePicker(), label=_("End date"), required=False
    )

    class Meta:
        model = Companies
        fields = [
            "declarative_structure",
            "label",
            "legal_status",
            "email",
            "repository_code",
            "additional_address",
            "street_number",
            "street",
            "postal_code",
            "municipality",
            "donation_object",
            "inkind_donation",
            "inkind_donation_description",
            "cash_donation",
            "cash_payment_type",
            "cheque_deposit_date",
            "date_start",
            "date_end",
            "comment",
        ]
