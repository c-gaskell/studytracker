from django.contrib.auth.views import LogoutView
from django.urls import include, path

from .views import MDLLoginView

urlpatterns = [
    path("login/", MDLLoginView.as_view()),
    path("", include("django.contrib.auth.urls")),
]
