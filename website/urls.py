from django.urls import path

from .views import AssignmentsPage, BaseView, CalendarPage, HomePage

urlpatterns = [
    path('', HomePage.as_view(), name="homepage"),
    path('test/', BaseView.as_view(), name="testpage"),
    path('calendar/', CalendarPage.as_view(), name="calendar"),
    path('assignments/', AssignmentsPage.as_view(), name="assignments")
]
