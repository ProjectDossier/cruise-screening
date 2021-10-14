from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
import simplejson as json
from django.utils import timezone
from flask import Markup
from utils.helpers import search

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
