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
            "password1",
            "password2",
        )

    email = forms.EmailField(
        widget=forms.EmailInput({"placeholder": "name@example.com"}),
        required=False,
        help_text="It is not required but it is the only way to recover your password if you forget it."
        "You will be able to add it later.",
    )

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
            "date_of_birth",
            "languages",
            "knowledge_areas",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.fields["email"].initial = self.instance.email
        self.fields["first_name"].initial = self.instance.first_name
        self.fields["last_name"].initial = self.instance.last_name
        self.fields["location"].initial = self.instance.location
        self.fields["allow_logging"].initial = self.instance.allow_logging

        if self.instance.id:
            self.fields["languages"].initial = self.instance.languages.all()
            self.fields["date_of_birth"].initial = self.instance.date_of_birth
            self.fields["knowledge_areas"].initial = self.instance.knowledge_areas.all()

    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "input bulma-calendar",
                "data-type": "date",
            },
        ),
        required=False,
    )
    allow_logging = forms.BooleanField(
        required=False,
        help_text="If you check this box, your search actions will be logged and will be used to \
        improve the quality of the search engine. You can change this setting at any time.",
    )
