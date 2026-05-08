from django.db import models
from django.forms import model_to_dict

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