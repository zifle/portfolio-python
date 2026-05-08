import json

from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

from portfolio.models import Category


class CategoryIndex(View):
    def get(self, request):
        cats = Category.objects.annotate(num_albums=Count('album'))
        cats_list = [cat.to_dict() for cat in cats]
        return JsonResponse(cats_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)
        data = json.loads(request.body.decode('utf-8'))
        if 'id' in data and data['id'] > 0:
            category = get_object_or_404(Category, pk=data['id'])
            category.name = data['name']
            category.order = data['order']
        else:
            category = Category.objects.create(name=data['name'], order=data['order'] or 0)
        category.save()

        data = category.to_dict()
        return JsonResponse(data)

class CategoryDetail(View):
    def delete(self, request, id):
        if not request.user.is_authenticated:
            return HttpResponse("Not logged in", status=401)
        category = get_object_or_404(Category, pk=id)
        category.delete()
        return HttpResponse("Deleted category", status=200)