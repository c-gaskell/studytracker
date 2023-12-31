from typing import Any, Dict, List
from pprint import pprint
from datetime import date, datetime, timedelta
from calendar import month_name

from decouple import config
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from .forms import AssignmentForm
from .models import Assignment, CalendarEvent


class BaseView(View):
    """Parent class for pages using the `website/base.html` template."""

    template = "website/base.html"
    pagetitle = "Base Template"

    def get_page_attrs(self, request: HttpRequest, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Get attributes shown in the page template.

        This method will provide attributes used by the base template.
        If a subclass needs to provide its own attributes, it should also call the super function.
        """
        attrs = {}

        attrs['ownername'] = User.objects.get(groups__name="admin").get_full_name()
        attrs['sitename'] = config("sitename")
        attrs['pagetitle'] = self.pagetitle
        return attrs

    def get(self, request: HttpRequest, **kwargs: Dict[str, Any]) -> HttpResponse:
        """HTTP GET Method.

        Generic method which will use get_page_attrs and self.template.
        If a subclass only needs custom attributes, just override get_page_attrs and not this method.
        """
        attrs = self.get_page_attrs(request, kwargs)
        return render(request, self.template, attrs)


class HomePage(BaseView):
    """Homepage dashboard."""

    template = "website/home.html"
    pagetitle = "Dashboard"

    def get_page_attrs(self, request: HttpRequest, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add events to homepage."""
        attrs = super().get_page_attrs(request, kwargs)

        if request.user.is_authenticated:
            attrs['events'] = CalendarEvent.today().filter(author=request.user)
            attrs['assignments'] = Assignment.objects.filter(creator=request.user, done=False)

        return attrs


class CalendarPage(BaseView):
    """Calendar Page."""

    template = "website/calendar.html"
    pagetitle = "Calendar"

    def get_page_attrs(self, request: HttpRequest, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().get_page_attrs(request, kwargs)

        currweek = timezone.now().isocalendar()[1]

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        attrs['weekdays'] = [
            f"{w} {date.fromisocalendar(timezone.now().year, currweek, d+1).day}" for d, w in enumerate(days)
        ]
        wstart = date.fromisocalendar(timezone.now().year, currweek, 1)
        attrs['month'] = f"{month_name[wstart.month]} {wstart.year}"

        attrs['hours'] = [(h * 60, f"{h:02d}:00") for h in range(24)]

        if request.user.is_authenticated:

            attrs['events'] = CalendarEvent.objects.filter(
                start_date__week=currweek,
                author=request.user,
            )

        return attrs


class AssignmentsPage(BaseView):
    """Assignments Page."""

    template = "website/assignments.html"
    pagetitle = "Assigments"

    def get_page_attrs(self, request: HttpRequest, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().get_page_attrs(request, kwargs)

        if request.user.is_authenticated:
            my_assignments = Assignment.objects.filter(creator=request.user, done=False)
            groups = [
                ("Overdue", my_assignments.filter(
                    due_date__lt=datetime.now(),
                ), "overdue"),
                ("Due Today", my_assignments.filter(
                    due_date__date=date.today(),
                    due_date__gte=datetime.now(),
                ), ""),
                ("Due This Week", my_assignments.filter(
                    due_date__gte=date.today() + timedelta(days=1),
                    due_date__lt=date.today() + timedelta(days=7),
                ), ""),
                ("Due Later", my_assignments.filter(
                    due_date__gte=date.today() + timedelta(days=7),
                ), ""),
                ("Completed", Assignment.objects.filter(creator=request.user, done=True), ""),
            ]

            attrs['groups'] = [(title, assignments, c) for title, assignments, c in groups if assignments]

        return attrs

    def post(self, request: HttpRequest) -> HttpResponse:
        """Recieve and process assignment done forms."""
        username = request.POST.get('user')
        id = request.POST.get('assignment')
        originpage = request.POST.get('origin')

        user = User.objects.get(username=username)
        assignment = Assignment.objects.get(creator=user, id=id)
        assignment.done = not assignment.done
        assignment.save()

        if originpage:
            return redirect(originpage)
        else:
            return self.get(request)


class AssignmentFormPage(BaseView):
    """Page to display the AssignmentForm."""

    template = "website/assignmentform.html"
    pagetitle = "Create or Edit Assignment"

    def get_page_attrs(self, request: HttpRequest, kwargs: Dict[str, Any], form: AssignmentForm = None) -> Dict[str, Any]:
        attrs = super().get_page_attrs(request, kwargs)

        try:
            form = AssignmentForm(instance=Assignment.objects.get(id=kwargs['id']))
        except KeyError:
            pass

        if form is None:
            attrs['form'] = AssignmentForm
        else:
            attrs['form'] = form

        return attrs

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        try:
            id = kwargs['id']
        except KeyError:
            form = AssignmentForm(request.POST)
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.creator = request.user
                assignment.save()
                return redirect('/assignments/')
            else:
                attrs = self.get_page_attrs(request, form=None)
                return render(request, self.template, attrs)
        else:
            assignment = Assignment.objects.get(id=id)
            form = AssignmentForm(request.POST, instance=assignment)
            form.save()
            return redirect('/assignments/')
