from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    BeneficiaryOrganization,
    Companies,
    CompanyLegalForms,
    DeclarativeStructure,
    PrivateIndividual,
)

# Register your models here.


class CompanyLegalFormsResource(resources.ModelResource):
    class Meta:
        model = CompanyLegalForms


class CompaniesResource(resources.ModelResource):
    class Meta:
        model = Companies


class PrivateIndividualResource(resources.ModelResource):
    class Meta:
        model = PrivateIndividual


admin.site.register(BeneficiaryOrganization, admin.ModelAdmin)
admin.site.register(DeclarativeStructure, admin.ModelAdmin)


@admin.register(Companies)
class CompaniesAdmin(ImportExportModelAdmin):
    resource_classes = [CompaniesResource]
    list_display = ("label", "date_start", "total_donation", "valid_date")
    # list_filter=['donation_nature']


@admin.register(CompanyLegalForms)
class CompanyLegalFormsAdmin(ImportExportModelAdmin):
    resource_classes = [CompanyLegalFormsResource]


@admin.register(PrivateIndividual)
class PrivateIndividualAdmin(ImportExportModelAdmin):
    resource_classes = [PrivateIndividualResource]
    list_display = (
        "full_name",
        "date_start",
        "cash_donation",
        "valid_date",
        "donation_nature",
    )
    list_filter = ["donation_nature"]
