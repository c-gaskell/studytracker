from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest


class MDLAuthenticationForm(AuthenticationForm):
    """Authentication form, with MDL styling."""

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs['class'] = "mdl-textfield__input"
        self.fields['password'].widget.attrs['class'] = "mdl-textfield__input"
