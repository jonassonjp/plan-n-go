"""
Plan N'Go — URLs do app accounts
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/",          views.register_view,      name="register"),
    path("confirm/<uuid:token>/", views.confirm_email_view, name="confirm_email"),
    path("profile/setup/",     views.profile_setup_view, name="profile_setup"),
    path("login/",             views.login_view,          name="login"),
    path("logout/",            views.logout_view,         name="logout"),
]
