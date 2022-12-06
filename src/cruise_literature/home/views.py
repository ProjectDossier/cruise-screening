from django.shortcuts import render


def home(request):
    """
    Home page
    """
    if request.method == "GET":
        return render(
            request,
            "home/home.html",
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
