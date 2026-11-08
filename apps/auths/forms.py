from unfold.forms import UserChangeForm as BaseUserChangeForm
from unfold.forms import UserCreationForm as BaseUserCreationForm

from apps.auths.models import User


class UserCreationForm(BaseUserCreationForm):
    """Add-user form for the email-based User (no username)."""

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")


class UserChangeForm(BaseUserChangeForm):
    """Change-user form for the email-based User (no username)."""

    class Meta(BaseUserChangeForm.Meta):
        model = User
        fields = "__all__"