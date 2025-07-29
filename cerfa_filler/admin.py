from django.contrib import admin
from .models import Companies, BeneficiaryOrganization
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.


class CompaniesResource(resources.ModelResource):

    class Meta:
        model = Companies


admin.site.register(BeneficiaryOrganization, admin.ModelAdmin)

@admin.register(Companies)
class CompaniesAdmin(ImportExportModelAdmin):
    resource_classes = [CompaniesResource]




