"""
Plan N'Go — Views principais (landing page)
"""

from django.shortcuts import render


def index(request):
    return render(request, "plango/index.html")
