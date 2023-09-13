from django.contrib.auth.views import LoginView
from django.shortcuts import render

from .forms import MDLAuthenticationForm


class MDLLoginView(LoginView):
    """Login view with MDL styling."""

    form_class = MDLAuthenticationForm
