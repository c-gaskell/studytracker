from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class AcYear(models.Model):
    """Academic Year."""

    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['start']


class Term(models.Model):
    """Term within a year."""

    name = models.CharField(max_length=255)
    year = models.ForeignKey(AcYear, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ['year', 'start']


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


class Topic(models.Model):
    """A topic within a module."""

    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)  # Creator determined via module
    order_id = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])

    class Meta:
        ordering = ["module", "-order_id", "name"]


class Assignment(models.Model):
    """A single assigment. Can be associated with a module."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True)

    # module is nullable so explicit relation to User is needed
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["due_date", "assigned_date", "name"]
