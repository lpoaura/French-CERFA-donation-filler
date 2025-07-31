import urllib.parse
from typing import Optional
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from num2words import num2words

# Create your models here.

# class PrivateIndividual(models.Model):

LEGAL_STATUSES = {
    "Asso": _("Association"),
    "Individual": _("Individual company"),
}

PAYMENT = {
    "Cash": _("Cash"),
    "Cheque": _("Cheque"),
    "Bank transfer": _("Bank transfer"),
    "Other": _("Other"),
}


class DeclarativeStructure(models.Model):
    label = models.CharField(max_length=15, verbose_name=_("Label"), unique=True)

    class Meta:
        verbose_name = _("Declarative structure")
        verbose_name_plural = _("Declarative structures")
        ordering = ("label",)

    def __str__(self):
        return self.label


class CompanyLegalForms(models.Model):
    code = models.CharField(max_length=4, verbose_name=_("Label"), unique=True)
    label = models.CharField(max_length=200, verbose_name=_("Label"), unique=True)

    class Meta:
        verbose_name = _("Legal form")
        verbose_name_plural = _("Legal forms")
        ordering = ("label",)

    def __str__(self):
        return self.label


class BaseOrganization(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True, primary_key=True)
    label = models.CharField(max_length=200, verbose_name=_("Label"))
    email = models.EmailField(null=True, blank=True)
    legal_status = models.ForeignKey(
        CompanyLegalForms,
        verbose_name=_("Legal status"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    repository_code = models.CharField(max_length=20, verbose_name=_("Repository code"))
    additional_address = models.CharField(
        max_length=200, verbose_name=_("Additional address"), blank=True, null=True
    )
    street_number = models.CharField(
        max_length=20, verbose_name=_("Street number"), blank=True, null=True
    )
    street = models.CharField(
        max_length=200, verbose_name=_("Street"), blank=True, null=True
    )
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal code"))
    municipality = models.CharField(max_length=200, verbose_name=_("Municipality"))

    class Meta:
        abstract = True


class BeneficiaryOrganization(BaseOrganization):
    object_description = models.CharField(
        max_length=200, verbose_name=_("Object"), default="", blank=True
    )
    sign_file = models.ImageField(
        verbose_name=_("Sign image file"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Beneficiary organization")
        verbose_name_plural = _("Beneficiary organization")

    def __str__(self):
        return self.label


class Companies(BaseOrganization):
    order = models.IntegerField(
        verbose_name=_("Order number"),
        editable=False,
        blank=True,
        null=True,
    )
    donation_object = models.CharField(
        max_length=200, verbose_name=_("Object"), null=True, blank=True
    )
    inkind_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("In-kind Donation"),
        blank=True,
        null=True,
    )
    inkind_donation_description = models.TextField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("In-kind Donation description"),
    )
    cash_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Cash Donation"),
        blank=True,
        null=True,
    )
    cash_payment_type = models.CharField(
        choices=PAYMENT, blank=True, null=True, verbose_name=_("Cash payment type")
    )
    cheque_deposit_date = models.DateField(
        null=True, blank=True, verbose_name=_("Cheque deposit date")
    )
    date_start = models.DateField(default=now, verbose_name=_("Initial donation date"))
    date_end = models.DateField(null=True, blank=True, verbose_name=_("End date"))
    valid_date = models.DateField(
        null=True, blank=True, verbose_name=_("Validation date")
    )
    comment = models.CharField(
        max_length=200, verbose_name=_("Comment"), null=True, blank=True
    )
    declarative_structure = models.ForeignKey(
        DeclarativeStructure,
        verbose_name=_("Declarative structure"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    timestamp_create = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_update = models.DateTimeField(auto_now=True, editable=False)

    @property
    def inkind_donation_as_text(self) -> Optional[str]:
        if self.inkind_donation:
            return num2words(self.inkind_donation, lang="fr", to="currency")

    @property
    def cash_donation_as_text(self) -> Optional[str]:
        if self.cash_donation:
            return num2words(self.cash_donation, lang="fr", to="currency")

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

    @property
    def year(self):
        return self.date_start.year

    @property
    def order_number(self):
        return f"{self.year}-PM-{self.order}"

    @property
    def mailto(self):
        formattedUrl = settings.SITE + reverse(
            "cerfa_filler:companies-cerfa-pdf", kwargs={"pk": self.uuid}
        )
        formattedBody = f"Hello,\n\nPlease find below a link to download your tax receipt for your donation.\n\n{formattedUrl}\n\nSincerely"
        formattedSubject = "Tax receipt for your donation"
        mailto = f"mailto:{self.email}?subject={formattedSubject}&body={urllib.parse.quote(formattedBody)}"
        return mailto

    def __str__(self):
        return f"{self.label} - {self.date_start} - {self.total_donation}"

    def save(self, *args, **kwargs):
        if not self.order:
            latest_record = (
                Companies.objects.filter(date_start__year=self.year)
                .order_by("order")
                .last()
            )
            self.order = latest_record.order + 1 if latest_record else 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        permissions = [
            ("change_validation", "Can change the validation status"),
            ("send_email", "Can send email"),
        ]
