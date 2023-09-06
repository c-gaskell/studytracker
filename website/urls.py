from django.urls import path

from .views import BaseView

urlpatterns = [
    path('test/', BaseView.as_view(), name="testpage"),
]
