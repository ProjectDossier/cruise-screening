from django.shortcuts import redirect, render

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
def view_organisations(request):
    """View all organisations."""
    organisations = Organisation.objects.all()
    return render(request, "organisations/view_all_organisations.html", {"organisations": organisations})


@login_required
def organisation_people_list(request):
    """View all people in an organisation."""
    return render(request, 'organisations/people_list.html')
