from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect

from .forms import NewUserForm, EditUserForm


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("home")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(
                request=request,
                template_name="users/register.html",
                context={"form": form},
            )

    if request.user.is_authenticated:
        return redirect("home")

    form = NewUserForm
    return render(
        request=request, template_name="users/register.html", context={"form": form}
    )


def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Logged out successfully!")
    return redirect("home")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request, template_name="users/login.html", context={"form": form}
    )


def user_profile(request):
    """
    User profile page
    """
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(
                request,
                "users/user_profile.html",
            )

    return HttpResponseNotFound("<h1>Page not found</h1>")


@login_required
def edit_profile(request):
    """
    Edit user profile page
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            form = EditUserForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Your profile was updated successfully.")
                return redirect("user_profile")
            else:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")

                return render(
                    request=request,
                    template_name="users/user_profile.html",
                    context={"form": form},
                )
        else:
            form = EditUserForm(
                initial={
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "email": request.user.email,
                    "location": request.user.location,
                    "allow_logging": request.user.allow_logging,
                    "preferred_taxonomies": request.user.preferred_taxonomies,
                }
            )
            return render(
                request=request,
                template_name="users/edit_user_profile.html",
                context={"form": form},
            )
