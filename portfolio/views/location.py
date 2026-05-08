import json

from django.db.models import Count
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from portfolio.models import Location


class LocationsIndex(View):
    def get(self, request):
        locs = Location.objects.annotate(num_albums=Count('album'))
        locs_list = [loc.to_dict() for loc in locs]
        return JsonResponse(locs_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)
        data = json.loads(request.body.decode('utf-8'))
        if 'id' in data and data['id'] > 0:
            location = get_object_or_404(Location, pk=data['id'])
            location.name = data['name']
            location.coordinate_lat = data['coordinate_lat']
            location.coordinate_lng = data['coordinate_lng']
        else:
            location = Location.objects.create(
                name=data['name'],
                coordinate_lat=data['coordinate_lat'],
                coordinate_lng=data['coordinate_lng'],
            )
        location.save()

        data = model_to_dict(location)
        return JsonResponse(data)