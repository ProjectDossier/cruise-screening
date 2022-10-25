from django.forms import ModelForm
from .models import Organisation, OrganisationMember

from django import forms
from django.forms import Textarea, ModelForm, TextInput, Form, FileField, Select, HiddenInput, CharField
from django.contrib.auth import get_user_model


class OrganisationForm(ModelForm):
    """Form for creating an organisation."""
    class Meta:
        model = Organisation
        fields = ["title", "description", "admins"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control"}),
        }
    admins = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(), widget=forms.CheckboxSelectMultiple, help_text="Select the users who will be administrators of this organisation."
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(OrganisationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        organisation = super(OrganisationForm, self).save(commit=False)
        organisation.created_by = self.user
        if commit:
            organisation.save()
            admins_list = list(self.cleaned_data['admins'])
            if self.user not in admins_list:
                admins_list.append(self.user)
            for _user in admins_list:
                member = OrganisationMember(
                    member=_user, organisation=organisation, role="AD"
                )
                member.save()

        return organisation


class OrganisationMemberForm(ModelForm):
    """Form for adding a member to an organisation."""
    class Meta:
        model = OrganisationMember
        fields = ["member", "role"]
        widgets = {
            "member": Select(attrs={"class": "form-control"}),
            "role": Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop("organisation", None)
        super(OrganisationMemberForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        org_member = super(OrganisationMemberForm, self).save(commit=False)
        org_member.organisation = self.organisation
        if commit:
            org_member.save()
        return org_member
