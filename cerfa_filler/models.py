from django.db import models
from django.utils.translation import gettext_lazy as _
from num2words import num2words
from datetime import datetime
from uuid import uuid4

# Create your models here.

# class PrivateIndividual(models.Model):

LEGAL_STATUSES = {
    "Asso": _("Association"),
    "Individual": _("Individual company"),
}

PAYMENT = {
    "Cash": _("Cahs"),
    "Cheque": _("Cheque"),
    "Bank transfer": _("Bank transfer"),
    "Other": _("Other"),
}


class Companies(models.Model):
    uuid = models.UUIDField(default=uuid4())
    label = models.CharField(max_length=200, verbose_name=_("Label"))
    legal_status = models.CharField(models.CharField, choices=LEGAL_STATUSES)
    repository_code = models.CharField(max_length=20, verbose_name=_("repository_code"))
    street_number = models.CharField(
        max_length=20, verbose_name=_("Street number"), blank=True, null=True
    )
    street = models.CharField(
        max_length=200, verbose_name=_("Street"), blank=True, null=True
    )
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal code"))
    municipality = models.CharField(max_length=200, verbose_name=_("Municipality"))
    inkind_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("In-kind Donation"),
        blank=True,
        null=True,
    )
    inkind_donation_description = models.TextField(
        max_length=500, blank=True, default=""
    )
    cash_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Cash Donation"),
        blank=True,
        null=True,
    )
    cash_payment_type = models.CharField(choices=PAYMENT, blank=True, null=True)
    date_start = models.DateField(default=datetime.now())
    end_date = models.DateField(default=datetime.now())
    export_date = models.DateField(null=True, blank=True)
    # cerfa_file = models.FileField(upload_to='exports')

    @property
    def inkind_donation_as_text(self):
        return num2words(self.inkind_donation or 0, lang="fr", to="currency")

    @property
    def cash_donation_as_text(self):
        return num2words(self.cash_donation or 0, lang="fr", to="currency")

    @property
    def total_donation_as_text(self):
        return num2words(
            self.total_donation,
            lang="fr",
            to="currency",
        )

    @property
    def total_donation(self):
        return (self.inkind_donation or 0) + (self.cash_donation or 0)

    def __str__(self):
        return f"{self.label} - {self.date_start} - {self.total_donation}"

