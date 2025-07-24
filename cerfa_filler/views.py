from django.shortcuts import render
from django.views.generic import DetailView

from .models import Companies

class CompaniesCerfa(DetailView):
    template_name = 'companies_cerfa.svg'
    model = Companies


