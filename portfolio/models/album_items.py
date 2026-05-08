from django.db import models

from .album_item import AlbumItem


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