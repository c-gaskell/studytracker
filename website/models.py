from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from datetime import timedelta
from math import ceil


class AcYear(models.Model):
    """Academic Year."""

    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['start']

    def __str__(self) -> str:
        return "AcYear " + self.name


class Term(models.Model):
    """Term within a year."""

    name = models.CharField(max_length=255)
    year = models.ForeignKey(AcYear, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ['year', 'start']

    def __str__(self) -> str:
        return "Term " + self.name + " in " + str(self.year)


class Professor(models.Model):
    """A prof or similar member of teaching staff."""

    title = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    contact_details = models.TextField(blank=True)
    location = models.TextField(blank=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_full_name(self) -> str:
        """Get full name."""
        if not self.first_name and not self.title:
            return "Professor " + self.last_name
        return (self.title + ". " if self.title else "") + \
            (self.first_name + " " if self.first_name else "") + \
            self.last_name

    class Meta:
        ordering = ["last_name", "first_name"]

    __str__ = get_full_name


class Module(models.Model):
    """A single module.

    May span multiple terms, but contained within a year.
    `terms` is nullable, so a module can be left without assigned terms.
    """

    name = models.CharField(max_length=255)
    year = models.ForeignKey(AcYear, on_delete=models.CASCADE)  # Creator determined via year
    terms = models.ManyToManyField(Term)
    professors = models.ManyToManyField(Professor)

    class Meta:
        ordering = ["year", "name"]

    def __str__(self) -> str:
        return "Module " + self.name


class Topic(models.Model):
    """A topic within a module."""

    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)  # Creator determined via module
    order_id = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])

    class Meta:
        ordering = ["module", "-order_id", "name"]

    def __str__(self) -> str:
        return "Topic " + self.name + " in " + str(self.module)


class Assignment(models.Model):
    """A single assigment. Can be associated with a module."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    done = models.BooleanField(default=False)

    # module is nullable so explicit relation to User is needed
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["due_date", "assigned_date", "name"]

    def __str__(self) -> str:
        if self.done:
            return "Completed assignment: " + self.name
        else:
            return "Assignment: " + self.name

    def get_description(self) -> str:
        if self.description:
            return self.description
        else:
            return "No Description..."


class EventType(models.Model):
    """Type of a calendar event."""

    name = models.CharField(max_length=255)
    color = models.CharField(max_length=6)  # Hex Color, without #. Case-insensitive
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CalendarEvent(models.Model):
    """An event on the calendar."""

    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    event_type = models.ForeignKey(EventType, null=True, on_delete=models.SET_NULL)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    repeat = models.BooleanField(default=False)
    repeat_until = models.DateField(null=True, blank=True)
    # Represents 7 booleans
    # - as binary, MSB is Monday, LSB is Sunday
    # 1 = repeats on this day, 0 = doesn't occur on this day.
    repeat_days = models.PositiveIntegerField(validators=[MaxValueValidator(127)], null=True, blank=True)

    location_name = models.TextField(blank=True)

    class Meta:
        ordering = ["start_date", "end_date"]

    def __str__(self) -> str:
        return self.name + " on " + self.start_date.isoformat()

    @classmethod
    def today(cls: "CalendarEvent") -> models.QuerySet:
        """Check if event is today."""
        return cls.objects.filter(
            start_date__gte=timezone.now().replace(hour=0, minute=0, second=0),
            end_date__lte=timezone.now().replace(hour=23, minute=59, second=59)
        )

    def start_min(self) -> int:
        """Return the start row in the CSS Grid Calendar."""
        return (self.start_date.hour * 60) + self.start_date.minute

    def end_min(self) -> int:
        """Return the end row in the CSS Grid Calendar."""
        if self.end_date.date() > self.start_date.date():
            end = self.start_date.replace(hour=23, minute=59)
        else:
            end = self.end_date

        return (end.hour * 60) + end.minute
