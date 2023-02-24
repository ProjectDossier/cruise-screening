from django.shortcuts import render
import random


def home(request):
    """
    Home page
    """
    if request.method == "GET":
        default_search_queries = [
            "Natural Language Processing",
            "Machine Learning",
            "Computational Biology",
            "Comparative Genomics",
            "High Energy Physics",
            "Cancer Research",
            "How to build a search engine?",
        ]
        return render(
            request,
            "home/home.html",
            {"default_query": random.choice(default_search_queries)},
        )


def about(request):
    """
    About page
    """
    if request.method == "GET":
        return render(
            request,
            "home/about.html",
        )


def faq(request):
    """
    FAQ page
    """
    if request.method == "GET":
        return render(
            request,
            "home/faq.html",
        )
