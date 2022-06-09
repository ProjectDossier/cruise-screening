from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Language


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "location",
            "languages",
            "knowledge_areas",
            "allow_logging",
            "password1",
            "password2",
        )

    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1900, 2010))
    )
    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)

        if commit:
            user.save()
            self.save_m2m()

        return user


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "location",
            "allow_logging",
            "preferred_taxonomies",
        )
