from django.urls import path

from . import views

app_name = 'literature_review'
urlpatterns = [
    path(
        "literature_review/",
        views.literature_review_home,
        name="literature_review_home",
    ),
    path('literature_review/<int:review_id>/', views.review_details, name='review_details'),
    path('screen_papers/<int:review_id>/', views.screen_papers, name='screen_papers'),
    path("create_review/", views.create_new_review, name="create_new_review"),
]
