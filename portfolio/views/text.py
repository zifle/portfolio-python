import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from portfolio.models import TextBox


class TextIndex(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Not logged in'}, status=401)

        data = json.loads(request.body.decode('utf-8'))

        id = data.pop('id') if 'id' in data else 0

        desc = data.pop('description') if 'description' in data else ''
        col_size = data.pop('col_size') if 'col_size' in data else 1

        if id and id > 0:
            textbox = get_object_or_404(TextBox, pk=id)
            textbox.description = desc
            textbox.col_size = col_size
        else:
            textbox = TextBox.objects.create(description=desc, col_size=col_size)

        textbox.save()
        data = textbox.to_dict()
        return JsonResponse(data)