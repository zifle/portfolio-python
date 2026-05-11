import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from portfolio.models import Image

@require_POST
def post_image_description(request, id:int):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)

    data = json.loads(request.body.decode('utf-8'))

    id = data.pop('id') if 'id' in data else id

    desc = data.pop('description') if 'description' in data else ''

    if id and id > 0:
        img = get_object_or_404(Image, pk=id)
        img.description = desc
        img.save()
        data = img.to_dict()
        return JsonResponse(data)