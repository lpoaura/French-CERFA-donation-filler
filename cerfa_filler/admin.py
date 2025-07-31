from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    BeneficiaryOrganization,
    Companies,
    CompanyLegalForms,
    DeclarativeStructure,
)

# Register your models here.


class CompanyLegalFormsResource(resources.ModelResource):
    class Meta:
        model = CompanyLegalForms


class CompaniesResource(resources.ModelResource):
    class Meta:
        model = Companies


admin.site.register(BeneficiaryOrganization, admin.ModelAdmin)
admin.site.register(DeclarativeStructure, admin.ModelAdmin)


@admin.register(Companies)
class CompaniesAdmin(ImportExportModelAdmin):
    resource_classes = [CompaniesResource]


@admin.register(CompanyLegalForms)
class CompanyLegalFormsAdmin(ImportExportModelAdmin):
    resource_classes = [CompanyLegalFormsResource]
