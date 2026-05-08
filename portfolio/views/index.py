from django.shortcuts import render


def index_view(request, resource):
    return render(request, 'dist/index.html', {})