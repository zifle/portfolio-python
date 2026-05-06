from django.db import models
from django.db.models import QuerySet, F
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.dispatch import receiver
from django.forms import model_to_dict
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel
from django.db.models.signals import pre_save

from portfolio.utils import get_mean_gps_position


# Create your models here.
class Camera(models.Model):
    class Meta:
        db_table = 'cameras'

    brand = models.CharField(
        "camera brand",
        max_length=20,
        help_text="Maker of the camera",
        # Example "FUJIFILM"
    )
    model = models.CharField(
        "camera model",
        max_length=10,
        help_text="Model of the camera",
        # Example "X-T3"
    )

    def __str__(self):
        return f'{self.brand} {self.model}'

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        if hasattr(self, 'num_images'):
            data['num_images'] = self.num_images

        return data

class Lens(models.Model):
    class Meta:
        db_table = 'lenses'

    brand = models.CharField(
        "lens brand",
        max_length=20,
        help_text="Maker of the lens",
        # Example "FUJIFILM"
    )
    model = models.CharField(
        "lens model",
        max_length=40,
        help_text="Model of the lens",
        # Example `XF18-55mmF2.8-4 R LM OIS`
    )

    def __str__(self):
        return f'{self.brand} {self.model}'

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        if hasattr(self, 'num_images'):
            data['num_images'] = self.num_images

        return data

class AlbumItem(PolymorphicModel):
    pass

class Image(AlbumItem):
    class Meta:
        db_table = 'images'

    path = models.CharField(
        max_length=200,
        help_text="Relative path to the base image (without resolution suffix)",
    )
    available_res = models.JSONField(
        "available resolutions",
        help_text="List of available resolutions of the image",
        blank=True,
    )
    max_width = models.IntegerField(
        help_text="Maximum width of the image",
    )
    max_height = models.IntegerField(
        help_text="Maximum height of the image",
    )
    description = models.TextField(
        "description",
        null=True,
        blank=True,
        default=None,
    )

    # Image metadata (fetched from exif)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    lens = models.ForeignKey(Lens, on_delete=models.SET_NULL, null=True, blank=True)
    date_taken = models.DateTimeField("date taken", null=True, blank=True)
    focal_length = models.IntegerField("focal length", null=True, blank=True)
    focal_length_35 = models.IntegerField(
        "35mm focal length",
        null=True,
        blank=True,
        help_text="Focal length in 35mm equivalent",
    )
    exposure_time = models.CharField(
        "exposure time",
        max_length=10,
        null=True,
        blank=True,
        help_text="Exposure time of photo",
    )
    exposure_compensation = models.DecimalField(
        "exposure compensation",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )
    aperture = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.path.format(self.available_res[-1])

    def get_paths(self) -> dict[int, str]:
        paths = {}
        for width in self.available_res:
            paths[width] = '/static/'+self.path.format(width)
        return paths

    def to_dict(self):
        data = model_to_dict(self)

        data['paths'] = self.get_paths()
        if hasattr(self, 'order'):
            data['order'] = self.order

        return data

class TextBox(AlbumItem):
    class Meta:
        db_table = 'text_boxes'

    description = models.TextField(null=False)
    col_size = models.IntegerField(
        "column size",
        default=1,
        help_text="Number of columns that the box should take up",
    )

    def __str__(self):
        desc = self.description
        if len(desc) > 23:
            desc = desc[:20]+'...'
        return desc

    def to_dict(self):
        data = model_to_dict(self)

        if hasattr(self, 'order'):
            data['order'] = self.order

        return data

class AlbumItems(models.Model):
    class Meta:
        db_table = "album_items"
        verbose_name_plural = "album items"
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['album', 'item'], name='unique_album_item'),
        ]

    album = models.ForeignKey("Album", on_delete=models.CASCADE)
    item = models.ForeignKey(AlbumItem, on_delete=models.CASCADE)
    order = models.IntegerField('order of the items', default=0)

    def __str__(self):
        return f'{self.album.title} - {self.item}'

class Location(models.Model):
    class Meta:
        db_table = "locations"

    name = models.CharField(max_length=100, )
    coordinate_lng = models.FloatField(
        "longitudinal coordinates",
        null=True,
        blank=True,
    )
    coordinate_lat = models.FloatField(
        "latitudinal coordinates",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} <{self.coordinate_lat},{self.coordinate_lng}>'

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        if hasattr(self, 'distance'):
            data['distance'] = self.distance
        if hasattr(self, 'num_albums'):
            data['num_albums'] = self.num_albums

        return data

    @classmethod
    def get_nearby(cls, gps_coords: list[tuple[float, float]]) -> QuerySet:
        """
        Given a list of (lat,long) tuples of coordinates, find an existing saved location
        within 1km of the point, and return the closest one (if multiple are found)
        """
        if len(gps_coords) == 0:
            return cls.objects.none()

        # SELECT
        #   name,
        #    ( 6371 * acos( cos( radians(57.046125) ) * cos( radians( locations.coordinate_lat ) )
        #    * cos( radians(locations.coordinate_lng) - radians(9.9310493)) + sin(radians(57.046125))
        #    * sin( radians(locations.coordinate_lat)))) AS distance
        # FROM locations
        # WHERE distance < 0.50
        # ORDER BY distance;
        max_distance_km = 10
        earth_radius_km = 6371
        pos_lat, pos_lng = get_mean_gps_position(gps_coords)
        where = (earth_radius_km * ACos(Cos(Radians(pos_lat)) * Cos(Radians(F('coordinate_lat')))
                                        * Cos(Radians(F('coordinate_lng')) - Radians(pos_lng)) + Sin(Radians(pos_lat))
                                        * Sin(Radians(F('coordinate_lat')))))

        locations = cls.objects.annotate(distance=where).filter(distance__lte=max_distance_km)

        return locations

class Category(models.Model):
    class Meta:
        db_table = "categories"

    name = models.CharField(max_length=100)
    order = models.IntegerField('order of the category', default=0)

    def __str__(self):
        return self.name

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        if hasattr(self, 'num_albums'):
            data['num_albums'] = self.num_albums

        return data

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

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        data['num_images'] = self.items.instance_of(Image).count()

        album_items = self.items.annotate(order=F('albumitems__order')).order_by('order')
        data['items'] = [item.to_dict() for item in album_items]

        return data

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