"""
Plan N'Go — URLs do app accounts
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/",          views.register_view,      name="register"),
    path("confirm/<uuid:token>/", views.confirm_email_view, name="confirm_email"),
    path("profile/setup/",     views.profile_setup_view, name="profile_setup"),
    path("login/",             views.login_view,          name="login"),
    path("logout/",            views.logout_view,         name="logout"),

    # Reset de senha
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset_form.html",
        email_template_name="accounts/password_reset_email.html",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url="/accounts/password-reset/done/",
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url="/accounts/reset/done/",
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html",
    ), name="password_reset_complete"),
]
