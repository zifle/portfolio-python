from django.contrib import admin

from portfolio.models import Lens, Camera, Album, Image, TextBox, AlbumItems

# Register your models here.
admin.site.register(Lens)
admin.site.register(Camera)
admin.site.register(Image)
admin.site.register(TextBox)
admin.site.register(AlbumItems)

class AlbumItemsInline(admin.TabularInline):
    model = AlbumItems
    extra = 0

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ['title']}),
        (None, {"fields": ['description']}),
        ("Dates", {
            "fields": ["date_start", "date_end"],
        }),
        ("Location", {
            "fields": [
                "location",
                "location_coordinate_lng",
                "location_coordinate_lat",
            ],
            "classes": ["collapse"],
        }),
    ]
    inlines = [AlbumItemsInline]
