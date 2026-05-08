from django.db import models
from django.forms import model_to_dict


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