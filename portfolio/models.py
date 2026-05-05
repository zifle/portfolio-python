from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel
from django.db.models.signals import pre_save

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

    def get_paths(self) -> list[str]:
        return [self.path.format(size) for size in self.available_res]

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

class AlbumItems(models.Model):
    class Meta:
        db_table = "album_items"
        verbose_name_plural = "album items"
        ordering = ['order']

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

class Category(models.Model):
    class Meta:
        db_table = "categories"

    name = models.CharField(max_length=100)
    order = models.IntegerField('order of the category', default=0)

    def __str__(self):
        return self.name

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

@receiver(pre_save, sender=Album)
def pre_save_receiver(sender, instance:Album, *args, **kwargs):
    # Update the slug, in case the title has been changed
    # (risks breaking links, but we don't want to keep old titles in slug)
    instance.slug = slugify(instance.title)