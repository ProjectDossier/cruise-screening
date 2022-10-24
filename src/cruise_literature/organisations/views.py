from django.shortcuts import redirect, render, get_object_or_404

# Create your views here.
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required

from organisations.forms import OrganisationForm
from organisations.models import Organisation


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
    return render(request, "organisations/view_all_organisations.html", {"organisations": organisations})


@login_required
def view_organisation(request, organisation_id):
    """View all people in an organisation."""
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    return render(request, 'organisations/view_organisation.html', {"organisation": organisation})


@login_required
def add_member(request):
    """Add a member to an organisation."""
    return render(request, 'organisations/view_organisation.html')


@login_required
def remove_member(request):
    """Remove a member from an organisation."""
    return render(request, 'organisations/view_organisation.html')