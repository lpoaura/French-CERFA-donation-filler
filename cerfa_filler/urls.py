from django.urls import path

from .views import CompaniesCerfa

urlpatterns = [
    path("cerfa/<int:pk>", CompaniesCerfa.as_view(), name="companies-cerfa"),
]