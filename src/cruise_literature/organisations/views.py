from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404

# Create your views here.
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required

from organisations.forms import OrganisationForm, OrganisationMemberForm
from organisations.models import Organisation, OrganisationMember
from users.models import User


@user_passes_test(lambda u: u.is_superuser)
@staff_member_required
def create_organisation(request):
    """View for creating an organisation."""
    if request.method == "POST":
        form = OrganisationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("organisations:view_organisations")
    else:
        form = OrganisationForm(user=request.user)
    return render(request, "organisations/create_organisation.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
@staff_member_required
def view_all_organisations(request):
    """View all organisations."""
    organisations = Organisation.objects.all()
    return render(
        request,
        "organisations/view_all_organisations.html",
        {"organisations": organisations},
    )


@login_required
def view_organisation(request, organisation_id):
    """View all people in an organisation."""
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    members = OrganisationMember.objects.filter(organisation=organisation)
    if not request.user.is_superuser and request.user not in organisation.members.all():
        return redirect("home")

    if request.user.is_superuser:
        current_user_role = "AD"
    else:
        current_user_role = OrganisationMember.objects.filter(
            member=request.user, organisation=organisation
        ).values_list("role", flat=True)[0]

    return render(
        request,
        "organisations/view_organisation.html",
        {"organisation": organisation, "members": members, "current_user_role":current_user_role},
    )


@login_required
def add_member(request, organisation_id):
    """Add a member to an organisation."""
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    if request.method == "POST":
        form = OrganisationMemberForm(request.POST, organisation=organisation)
        if form.is_valid():
            form.save()
            return redirect(
                "organisations:view_organisation", organisation_id=organisation_id
            )
    else:
        form = OrganisationMemberForm(organisation=organisation)
        form.fields["member"].queryset = User.objects.exclude(
            om_through__organisation=organisation
        )
    return render(
        request,
        "organisations/add_member.html",
        {"form": form, "organisation": organisation},
    )


@login_required
def remove_member(request, organisation_id, user_id):
    """Remove a member from an organisation."""
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    if request.method == "GET":
        user = get_object_or_404(User, pk=user_id)
        organisation.remove_user(user=user)
        return redirect(
            "organisations:view_organisation", organisation_id=organisation_id
        )
    return redirect("organisations:view_organisation", organisation_id=organisation_id)


def delete_organisation(request, organisation_id):
    """Delete an organisation."""
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    if request.method == "GET":
        organisation.delete()
        return redirect("organisations:view_all_organisations")
    return redirect("organisations:view_all_organisations")


def find_organisations(request, user_id):
    """Find organisations for a user and returns json."""
    user = get_object_or_404(User, pk=user_id)
    organisations = Organisation.objects.filter(members=user)
    return JsonResponse(
        [
            {"id": organisation.id, "title": organisation.title}
            for organisation in organisations
        ], safe=False
    )
