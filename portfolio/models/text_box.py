from django.db import models
from django.forms import model_to_dict
from .album_item import AlbumItem


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