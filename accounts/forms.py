from django.contrib.auth.forms import (
    UserCreationForm, 
    UserChangeForm,
    UsernameField
    )
from accounts.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser 
        fields = (
            "username",
            "email"
        )
        field_classes = {"username": UsernameField}

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser 
        fields = (
            "username",
            "email"
        )
        field_classes = {"username": UsernameField}