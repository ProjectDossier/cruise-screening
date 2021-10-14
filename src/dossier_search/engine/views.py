from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
import simplejson as json
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def index(request):
    """
    starting index page

    """
    if request.method == "GET":
        return render(
            request,
            "interfaces/welcome.html",
        )


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            login(request, user)
            return redirect("index")
        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])

            return render(
                request=request,
                template_name="users/register.html",
                context={"form": form},
            )

    form = UserCreationForm
    return render(
        request=request, template_name="users/register.html", context={"form": form}
    )


def home(request):

    if request.method == "GET":
        return render(request, "interfaces/home.html")
