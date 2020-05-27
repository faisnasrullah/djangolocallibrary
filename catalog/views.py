from django.shortcuts import render
from django.views import generic


# Create your views here.
class CatalogView(generic.ListView):
    template_name = "catalog/index.html"
