import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from portfolio.models import Album, Category, Location


class AlbumIndex(View):
    def get(self, request):
        if request.user.is_authenticated:
            albums = Album.objects.all()
        else:
            albums = Album.objects.filter(published=True)

        album_list = [album.to_dict(exclude=['items']) for album in albums]
        return JsonResponse(album_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        data = json.loads(request.body.decode('utf-8'))

        if 'category' in data and data['category'] is not None and data['category'] > 0:
            data['category'] = get_object_or_404(Category, pk=data['category'])
        else:
            data['category'] = None

        if 'location' in data and data['location'] is not None and data['location'] > 0:
            data['location'] = get_object_or_404(Location, pk=data['location'])
        else:
            data['location'] = None

        items = []
        if 'items' in data:
            items = data.pop('items')

        id = data.pop('id') if 'id' in data else 0

        if id and id > 0:
            album = get_object_or_404(Album, pk=id)
            for attr, value in data.items():
                setattr(album, attr, value)
        else:
            album = Album.objects.create(**data)

        album.save()
        album.set_album_items(items)

        data = album.get_detailed_dict()
        return JsonResponse(data)

class AlbumDetail(View):
    def get(self, request, id):
        album = None
        if isinstance(id, int):
            album = get_object_or_404(Album, pk=id)
        elif isinstance(id, str):
            album = Album.objects.get(slug=id)
        if not album:
            return JsonResponse({'error': 'Album not found'}, status=404)

        data = album.get_detailed_dict()
        return JsonResponse(data, safe=False)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        album = get_object_or_404(Album, pk=id)
        if album.published:
            return JsonResponse({"message": "Published albums cannot be deleted"}, status=400)

        album.delete()
        return JsonResponse({"success": True})

@ensure_csrf_cookie
@require_http_methods(['POST'])
def album_toggle_publish(request, id:int):
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in", status=401)
    album = get_object_or_404(Album, pk=id)
    data = json.loads(request.body.decode('utf-8'))
    if data['publish'] == True:
        album.published = True
    else:
        album.published = False
    album.save()
    return JsonResponse({"success": True})