from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
import simplejson as json
from django.utils import timezone
from utils.helpers import search
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import NewUserForm

# Create your views here.


def index(request):
    """
    starting index page

    """
    if request.method == "GET":
        query = 'The appellant on February 9, 1961 was appointed as an Officer in Grade III in the respondent Bank ( for short).'
        index = 'whole_doc_w_summ_intro'
        top_k = 1
        candidate_list = search(query, index, top_k)
        return render(
            request,
            "interfaces/welcome.html",
        )


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

    form = NewUserForm
    return render(
        request=request, template_name="users/register.html", context={"form": form}
    )


def logout_request(request):
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


def home(request):
    if request.method == "GET":
        return render(request, "interfaces/home.html")
