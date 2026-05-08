from django.test import TestCase
from django.utils.text import slugify

from portfolio.models import Album


class AlbumModelTests(TestCase):
    def test_automatic_slug_creation_simple(self):
        title = 'simple'

        album = Album.objects.create(title=title)

        self.assertEqual(album.title, 'simple')
        self.assertEqual(album.slug, 'simple')

    def test_slugified_title(self):
        title = 'Title with spaces'
        slugified = slugify(title)

        album = Album.objects.create(title=title)

        self.assertEqual(album.title, title)
        self.assertEqual(album.slug, slugified)
