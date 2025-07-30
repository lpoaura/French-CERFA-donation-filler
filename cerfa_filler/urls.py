from django.urls import path

from .views import (CompaniesCerfa, CompaniesCerfaToPdf, CompaniesCreateView,
                    CompaniesListView, CompaniesUpdateView, Home)

app_name = "cerfa_filler"

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("companies/cerfa/<uuid:pk>", CompaniesCerfa.as_view(), name="companies-cerfa"),
    path(
        "companies/cerfa/pdf/<uuid:pk>",
        CompaniesCerfaToPdf.as_view(),
        name="companies-cerfa-pdf",
    ),
    path("companies/list/", CompaniesListView.as_view(), name="companies-list"),
    path("companies/create/", CompaniesCreateView.as_view(), name="companies-create"),
    path(
        "companies/update/<uuid:pk>/",
        CompaniesUpdateView.as_view(),
        name="companies-update",
    ),
]
