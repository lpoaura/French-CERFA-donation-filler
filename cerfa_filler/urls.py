from django.urls import path

from .views import (
    CompaniesCerfaToPdf,
    CompaniesCreateView,
    CompaniesListView,
    CompaniesUpdateValidDateView,
    CompaniesUpdateView,
    Home,
    PrivateIndividualCerfaToPdf,
    PrivateIndividualCreateView,
    PrivateIndividualListView,
    PrivateIndividualUpdateValidDateView,
    PrivateIndividualUpdateView,
)

app_name = "cerfa_filler"

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path(
        "companies/cerfa/pdf/<uuid:pk>",
        CompaniesCerfaToPdf.as_view(),
        name="companies-cerfa-pdf",
    ),
    path(
        "companies/list/", CompaniesListView.as_view(), name="companies-list"
    ),
    path(
        "companies/create/",
        CompaniesCreateView.as_view(),
        name="companies-create",
    ),
    path(
        "companies/update/<uuid:pk>/",
        CompaniesUpdateView.as_view(),
        name="companies-update",
    ),
    path(
        "companies/update-valid-date/",
        CompaniesUpdateValidDateView.as_view(),
        name="update-valid-date",
    ),
    # Individuals
    path(
        "individuals/cerfa/pdf/<uuid:pk>",
        PrivateIndividualCerfaToPdf.as_view(),
        name="private-individual-cerfa-pdf",
    ),
    path(
        "individuals/list/",
        PrivateIndividualListView.as_view(),
        name="private-individual-list",
    ),
    path(
        "individuals/create/",
        PrivateIndividualCreateView.as_view(),
        name="private-individual-create",
    ),
    path(
        "individuals/update/<uuid:pk>/",
        PrivateIndividualUpdateView.as_view(),
        name="private-individual-update",
    ),
    path(
        "individuals/update-valid-date/",
        PrivateIndividualUpdateValidDateView.as_view(),
        name="update-valid-date",
    ),
]
