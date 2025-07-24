from django.urls import path

from .views import CompaniesCerfa, CompaniesCerfaToPdf

urlpatterns = [
    path("cerfa/<int:pk>", CompaniesCerfa.as_view(), name="companies-cerfa"),
    path("cerfa/pdf/<int:pk>", CompaniesCerfaToPdf.as_view(), name="companies-cerfa"),
]