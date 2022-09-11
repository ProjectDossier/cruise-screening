from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .forms import NewLiteratureReviewForm
from .models import LiteratureReview


def create_new_review(request):
    if request.method == "POST":
        form = NewLiteratureReviewForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get("title")
            messages.success(request, f"New review created: {title}")
            return redirect("home")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(
                request=request,
                template_name="literature_review/create_literature_review.html",
                context={"form": form},
            )

    if not request.user.is_authenticated:
        return redirect("home")

    form = NewLiteratureReviewForm(user=request.user)
    return render(
        request=request,
        template_name="literature_review/create_literature_review.html",
        context={"form": form},
    )


def literature_review_home(request):
    context = {}
    context["literature_reviews"] = LiteratureReview.objects.filter(
        members=request.user
    )

    return render(
        request=request, template_name="literature_review/home.html", context=context
    )


def review_details(request, review_id):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user in review.members.all():
        return render(request, 'literature_review/view_review.html', {'review': review})
    else:
        return redirect("home")

