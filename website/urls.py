from django.urls import path

from .views import BaseView, HomePage

urlpatterns = [
    path('', HomePage.as_view(), name="homepage"),
    path('test/', BaseView.as_view(), name="testpage"),
]
