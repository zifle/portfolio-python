from django.db import models
from django.forms import model_to_dict

from .album_item import AlbumItem
from .camera import Camera
from .lens import Lens


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