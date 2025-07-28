from django.contrib import admin
from .models import Companies
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class BookResource(resources.ModelResource):

    class Meta:
        model = Companies

@admin.register(Companies)
class BookAdmin(ImportExportModelAdmin):
    resource_classes = [BookResource]

# admin.site.register(Companies, admin.ModelAdmin)


