# forms.py
from django import forms
from django.forms import DateInput
from multi_email_field.forms import MultiEmailField

from .models import Companies, DeclarativeStructure, PrivateIndividual


class DatePicker(DateInput):
    input_type = "date"

    def format_value(self, value):
        return (
            value.isoformat()
            if value is not None and hasattr(value, "isoformat")
            else ""
        )


class FilterForm(forms.Form):
    year = forms.ChoiceField(
        choices=[
            ("", "---------"),
        ]
        + [
            (year["date_start__year"], year["date_start__year"])
            for year in Companies.objects.order_by("date_start__year")
            .values("date_start__year")
            .distinct()
        ],
        required=False,
        label="Sélectionnez une année",
    )
    declarative_structure = forms.ModelChoiceField(
        queryset=DeclarativeStructure.objects.all(),
        required=False,
        label="Sélectionnez une structure déclarative",
    )
    validation = forms.ChoiceField(
        choices=[("", "---------"), (True, "Validé"), (False, "Non validé")],
        required=False,
        label="Statut de validation",
    )


class CompaniesForm(forms.ModelForm):
    date_start = forms.DateField(widget=DatePicker(), label="Date de début")
    date_end = forms.DateField(
        widget=DatePicker(), label="Date de fin", required=False
    )
    emails = MultiEmailField(required=False)

    class Meta:
        model = Companies
        fields = [
            "declarative_structure",
            "label",
            "legal_status",
            "emails",
            "repository_code",
            "street_number",
            "street",
            "additional_address",
            "postal_code",
            "municipality",
            "donation_object",
            "cash_donation",
            "cash_payment_type",
            "inkind_donation",
            "inkind_donation_description",
            "cheque_deposit_date",
            "date_start",
            "date_end",
            "comment",
        ]


class PrivateIndividualForm(forms.ModelForm):
    date_start = forms.DateField(widget=DatePicker(), label="Date du don")
    emails = MultiEmailField(required=False)

    class Meta:
        model = PrivateIndividual
        fields = [
            "declarative_structure",
            "first_name",
            "last_name",
            "emails",
            "street_number",
            "street",
            "additional_address",
            "postal_code",
            "municipality",
            "donation_object",
            "donation_nature",
            "cash_donation",
            "cash_payment_type",
            "date_start",
            "comment",
        ]
