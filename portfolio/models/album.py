from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.utils.text import slugify

from .image import Image
from .album_item import AlbumItem
from .album_items import AlbumItems
from .location import Location
from .category import Category


class Album(models.Model):
    class Meta:
        db_table = 'albums'

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, help_text="Event location", on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    date_start = models.DateField("start date", null=True, blank=True)
    date_end = models.DateField("end date", null=True, blank=True)
    published = models.BooleanField("published", default=True)

    items = models.ManyToManyField(
        AlbumItem,
        through=AlbumItems,
        help_text="Items of the album (photos and text)",
    )

    def __str__(self):
        return self.title

    def to_dict(self, fields=None, exclude=None) -> dict:
        data = model_to_dict(self, fields=fields, exclude=exclude)

        return data

    def get_tags(self, items = None) -> list[str]:
        tags = []

        if self.category:
            tags.append(str(self.category))
        if self.location:
            tags.append(str(self.location))
        if self.date_start and self.date_end:
            if self.date_start == self.date_end:
                tags.append('One-day')
            else:
                tags.append('Multiple days')

        cameras = set()
        lenses = set()
        if not items:
            items = self.items.instance_of(Image).prefetch_related('camera').prefetch_related('lens')
        for im in items:
            if im.camera:
                cameras.add(im.camera)
            if im.lens:
                lenses.add(im.lens)

        for cam in cameras:
            tags.append(str(cam))
        for lens in lenses:
            tags.append(str(lens))

        return tags

    def set_album_items(self, items_data: list[dict]):
        """
        Use a list of {'id': AlbumItem.id, 'order': AlbumItems.order} dicts
        to _set_ the related items on the album. Any items not specified will
        be deleted
        """
        existing = {ai.item_id: ai for ai in AlbumItems.objects.filter(album=self)}

        to_update = []
        to_create = []
        incoming_ids = set()

        for item in items_data:
            item_id = item['id']
            item_order = item['order']
            incoming_ids.add(item_id)

            if item_id in existing:
                ai = existing[item_id]
                ai.order = item_order
                to_update.append(ai)
            else:
                to_create.append(AlbumItems(album=self, item_id=item_id, order=item_order))

        AlbumItems.objects.filter(album=self).exclude(item_id__in=incoming_ids).delete()

        if to_update:
            AlbumItems.objects.bulk_update(to_update, ['order'])
        if to_create:
            AlbumItems.objects.bulk_create(to_create)

@receiver(pre_save, sender=Album)
def pre_save_receiver(sender, instance:Album, *args, **kwargs):
    # Update the slug, in case the title has been changed
    # (risks breaking links, but we don't want to keep old titles in slug)
    instance.slug = slugify(instance.title)