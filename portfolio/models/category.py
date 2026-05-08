from django.db import models
from django.forms import model_to_dict


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