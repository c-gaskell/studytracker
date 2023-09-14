from typing import Any, Dict

from decouple import config
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from .models import CalendarEvent


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
        attrs = super().get_page_attrs(request, kwargs)

        attrs['events'] = CalendarEvent.today().filter(author=request.user)

        return attrs
