import urllib.parse
from typing import Optional
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.timezone import localtime as _localtime
from django.utils.timezone import now
from multi_email_field.fields import MultiEmailField
from num2words import num2words


def localtime(value):
    """
    Renders a <time> element with an ISO 8601 datetime and a fallback display value.
    Example:
      {{ comment.added|localtime }}
    Outputs:
      <time datetime="2024-05-19T10:34:00+02:00" class="local-time">May 19, 2024 at 10:34 AM</time>
    """
    if not value:
        return ""

    localized = _localtime(value)

    return date(localized, "F j, Y \\a\\t g:i A")


PAYMENT = {
    "Cash": "Espèce",
    "Cheque": "Chèque",
    "CB": "Carte bancaire",
    "Bank transfer": "Virement",
    "Other": "Autre",
}

DONATION_NATURE = {
    "Cash": "Don en numéraire",
    "Waiver": "Abandon de frais",
}


class BaseModel(models.Model):
    timestamp_create = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_update = models.DateTimeField(auto_now=True, editable=False)
    comment = models.CharField(
        max_length=200, verbose_name="Commentaire", null=True, blank=True
    )

    class Meta:
        abstract = True


class EmailBaseModel(models.Model):
    emails = MultiEmailField(null=True, blank=True, default=[])

    class Meta:
        abstract = True

    @property
    def mailto(self):
        formattedBody = (
            "Bonjour,\n\nVeuillez trouver ci-dessous le lien pour récupérer"
            " le reçu fiscal suite à votre don à la LPO AuRA.\n\nEn vous remerciant"
            f" pour votre soutien et votre générosité.\n\n{self.cerfa_url}\n\n"
            "Je reste à votre disposition si nécessaire.\nBien cordialement,"
        )
        formattedSubject = "Reçu fiscal LPO AuRA"
        mailto = (
            f"mailto:{','.join(self.emails)}?subject={formattedSubject}"
            f"&body={urllib.parse.quote(formattedBody)}"
        )
        return mailto


class DeclarativeStructure(models.Model):
    label = models.CharField(max_length=15, verbose_name="Nom", unique=True)

    class Meta:
        verbose_name = "Délégation territoriale"
        verbose_name_plural = "Délégations territoriales"
        ordering = ("label",)

    def __str__(self):
        return self.label


class CompanyLegalForms(models.Model):
    code = models.CharField(max_length=4, verbose_name="Code", unique=True)
    label = models.CharField(max_length=200, verbose_name="Nom", unique=True)

    class Meta:
        verbose_name = "Forme légale"
        verbose_name_plural = "Formes légales"
        ordering = ("label",)

    def __str__(self):
        return self.label


class AddressBaseModel(models.Model):
    additional_address = models.CharField(
        max_length=200,
        verbose_name="Complément d'addresse",
        blank=True,
        null=True,
    )
    street_number = models.CharField(
        max_length=20, verbose_name="Numéro de rue", blank=True, null=True
    )
    street = models.CharField(
        max_length=200, verbose_name="Rue", blank=True, null=True
    )
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    municipality = models.CharField(max_length=200, verbose_name="Commune")

    class Meta:
        abstract = True


class BaseOrganization(BaseModel, AddressBaseModel):
    uuid = models.UUIDField(default=uuid4, unique=True, primary_key=True)
    label = models.CharField(max_length=200, verbose_name="Nom")
    emails = MultiEmailField(null=True, blank=True, default=[])
    legal_status = models.ForeignKey(
        CompanyLegalForms,
        verbose_name="Forme juridique",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    repository_code = models.CharField(max_length=20, verbose_name="SIRET")

    class Meta:
        abstract = True


class BeneficiaryOrganization(BaseOrganization, AddressBaseModel):
    object_description = models.CharField(
        max_length=200, verbose_name="Description", default="", blank=True
    )
    sign_file = models.ImageField(
        verbose_name="Image de la signature (PNG requis)",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Organisme bénéficiaire"
        verbose_name_plural = "Organismes bénéficiaires"

    def __str__(self):
        return self.label


class CashDonationBaseModel(models.Model):
    cash_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant du don en numéraire",
        blank=True,
        null=True,
    )
    cash_payment_type = models.CharField(
        choices=PAYMENT,
        blank=True,
        null=True,
        verbose_name="Type de paiement",
    )
    cheque_deposit_date = models.DateField(
        null=True, blank=True, verbose_name="Date de dépôt de chèque"
    )

    class Meta:
        abstract = True

    @property
    def cash_donation_as_text(self) -> Optional[str]:
        if self.cash_donation:
            return num2words(self.cash_donation, lang="fr", to="currency")


class InkindDonationBaseModel(models.Model):
    inkind_donation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valeur du don en nature",
        blank=True,
        null=True,
    )
    inkind_donation_description = models.TextField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Description du don en nature",
    )

    class Meta:
        abstract = True

    @property
    def inkind_donation_as_text(self) -> Optional[str]:
        if self.inkind_donation:
            return num2words(self.inkind_donation, lang="fr", to="currency")


class CashAndInkindDonationBaseModel(
    CashDonationBaseModel, InkindDonationBaseModel
):
    class Meta:
        abstract = True

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


class DonationMetadataBaseModel(models.Model):
    order = models.IntegerField(
        verbose_name="Numéro d'ordre",
        editable=False,
        blank=True,
        null=True,
    )
    donation_object = models.CharField(
        max_length=200,
        verbose_name="Objet de la donation",
        null=True,
        blank=True,
    )
    date_start = models.DateField(
        default=now, verbose_name="Date du don ou du début de donation"
    )
    date_end = models.DateField(
        null=True, blank=True, verbose_name="Date de fin de la donation"
    )
    valid_date = models.DateField(
        null=True, blank=True, verbose_name="Validation date"
    )
    declarative_structure = models.ForeignKey(
        DeclarativeStructure,
        verbose_name="Délégation territoriale",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    @property
    def year(self):
        return self.date_start.year

    @property
    def order_number(self):
        return f"{self.year}-PM-{self.order}"

    def save(self, *args, **kwargs):
        if not self.order:
            current_model = self.__class__
            latest_record = (
                current_model.objects.filter(date_start__year=self.year)
                .order_by("order")
                .last()
            )
            self.order = latest_record.order + 1 if latest_record else 1
        super().save(*args, **kwargs)


class Companies(
    BaseOrganization,
    DonationMetadataBaseModel,
    AddressBaseModel,
    CashAndInkindDonationBaseModel,
):
    def __str__(self):
        return f"{self.label} - {self.date_start} - {self.total_donation}"

    @property
    def metadata(self) -> Optional[str]:
        if self.timestamp_update:
            return f"Créé le {localtime(self.timestamp_create)}, mis à jour le {localtime(self.timestamp_update)}"

        else:
            return f"Créé le {localtime(self.timestamp_create)}"

    class Meta:
        verbose_name = "Personne morale"
        verbose_name_plural = "Personnes morales"
        permissions = [
            ("change_validation", "Can change the validation status"),
            ("send_email", "Can send email"),
        ]

    @property
    def cerfa_url(self):
        return settings.SITE + reverse(
            "cerfa_filler:companies-cerfa-pdf", kwargs={"pk": self.uuid}
        )


class PrivateIndividual(
    BaseModel,
    AddressBaseModel,
    CashDonationBaseModel,
    EmailBaseModel,
    DonationMetadataBaseModel,
):
    uuid = models.UUIDField(default=uuid4, unique=True, primary_key=True)
    first_name = models.CharField(max_length=200, verbose_name="Prénom")
    last_name = models.CharField(max_length=200, verbose_name="Nom")
    donation_nature = models.CharField(
        choices=DONATION_NATURE,
        default="Cash",
        verbose_name="Nature du don",
    )

    class Meta:
        verbose_name = "Particulier"
        verbose_name_plural = "Particuliers"
        permissions = [
            ("change_validation", "Can change the validation status"),
            ("send_email", "Can send email"),
        ]

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def cerfa_url(self):
        return settings.SITE + reverse(
            "cerfa_filler:private-individual-cerfa-pdf",
            kwargs={"pk": self.uuid},
        )
