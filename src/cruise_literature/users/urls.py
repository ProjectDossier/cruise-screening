from django.urls import path

from . import views
from . import api
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", views.register, name="register"),
    path("logout/", views.logout_request, name="logout"),
    path("login/", views.login_request, name="login"),
    path("accounts/login/", views.login_request, name="login"),
    path("profile", views.user_profile, name="user_profile"),
    path("edit_user_profile", views.edit_profile, name="edit_user_profile"),
    path("delete_user", views.delete_user, name="delete_user"),
    
    path('api/register/', api.register_api, name='register'),
    path('api/login/', api.login_request_api, name='login'),
    path('api/logout/', api.logout_request_api, name='logout'),
    path('api/delete/', api.delete_user_api, name='delete_user'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
