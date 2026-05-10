from datetime import datetime

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

    def has_duplicate(self) -> AlbumItem|None:
        """
        Check the DB for a saved Image with the same filename and date_taken.
        If there's a match, it's most likely the same exact image being reuploaded,
        and we can simply return the existing image instance instead of handling it again.
        """
        path = self.path.split('/')[1]
        date_taken = self.date_taken
        try:
            existing = Image.objects.get(date_taken=date_taken, path__endswith=path)
            return existing
        except Image.DoesNotExist:
            pass
        except Image.MultipleObjectsReturned:
            return Image.objects.filter(date_taken=date_taken, path__endswith=path).first()
        return None

    def set_exif_params(self, exif: dict[str, None|str|float|int]):
        if 'Make' in exif and 'Model' in exif:
            camera_brand = str(exif['Make'])
            camera_model = str(exif['Model'])
            if len(camera_brand) > 0 and len(camera_model) > 0:
                camera, _ = Camera.objects.get_or_create(brand=camera_brand, model=camera_model)
                self.camera = camera

        if 'LensMake' in exif:
            lens_brand = str(exif['LensMake']).strip()
            lens_model = str(exif['LensModel']).strip(' \u0000')
            if len(lens_brand) > 0 and len(lens_model) > 0:
                lens, _ = Lens.objects.get_or_create(brand=lens_brand, model=lens_model)
                self.lens = lens

        try:
            date_taken = None
            if 'DateTimeOriginal' in exif:
                date_taken = exif['DateTimeOriginal']
            elif 'DateTime' in exif:
                date_taken = exif['DateTime']
            elif 'DateTimeDigitized' in exif:
                date_taken = exif['DateTimeDigitized']

            if 'OffsetTimeOriginal' in exif:
                time_offset = exif['OffsetTimeOriginal']
            elif 'OffsetTime' in exif:
                time_offset = exif['OffsetTime']
            else:
                time_offset = '+0000'

            if date_taken:
                # Create a UTC Datetime from the two values
                dt = f'{date_taken} {time_offset.replace(':', '')}'
                date = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S %z')
                self.date_taken = date
        except KeyError:
            pass

        if 'FocalLength' in exif:
            self.focal_length = exif['FocalLength']

        if 'FocalLengthIn35mmFilm' in exif:
            self.focal_length_35 = exif['FocalLengthIn35mmFilm']

        if 'ExposureTime' in exif:
            val = exif['ExposureTime']
            self.exposure_time = f'1/{round(1/val)}'

        if 'ExposureBiasValue' in exif:
            self.exposure_compensation = exif['ExposureBiasValue']

        if 'FNumber' in exif:
            self.aperture = exif['FNumber']