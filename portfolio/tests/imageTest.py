from django.test import TestCase

from portfolio.models import Image


class ImageModelTests(TestCase):
    def test_has_duplicate(self):
        fields = {
            'path': 'path/image1.jpeg',
            'date_taken': '2020-01-01 12:00:00+0000',
            'available_res': [],
            'max_width': 0,
            'max_height': 0,
        }
        i1 = Image(**fields)
        i2 = Image(**fields)
        i1.save()

        has_duplicate = i2.has_duplicate()

        self.assertIsNotNone(has_duplicate)

    def test_not_duplicate_image(self):
        fields = {
            'path': 'path/image1.jpeg',
            'date_taken': '2020-01-01 12:00:00+0000',
            'available_res': [],
            'max_width': 0,
            'max_height': 0,
        }
        i1 = Image(**fields)
        i1.save()
        fields['date_taken'] = '2020-01-01 12:00:01+0000'
        i2 = Image(**fields)

        fields['path'] = 'path/image2.jpeg'
        fields['date_taken'] = i1.date_taken
        i3 = Image(**fields)

        i2_has_duplicate = i2.has_duplicate()
        i3_has_duplicate = i3.has_duplicate()

        self.assertIsNone(i2_has_duplicate)
        self.assertIsNone(i3_has_duplicate)