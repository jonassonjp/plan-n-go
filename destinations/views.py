"""
Plan N'Go — Views do app destinations (stub)
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "destinations/dashboard.html", {
        "destinations": [],
    })


@login_required
def create(request):
    return redirect("destinations:dashboard")


@login_required
def delete(request, pk):
    return redirect("destinations:dashboard")
