from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
import simplejson as json
from django.utils import timezone

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
