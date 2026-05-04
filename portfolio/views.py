from django.shortcuts import render, get_object_or_404
from django.views import generic

from portfolio.models import Album


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'portfolio/index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.all()

class AlbumView(generic.DetailView):
    template_name = 'portfolio/album.html'
    model = Album
