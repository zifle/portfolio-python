from datetime import datetime

from django.core.files.storage import storages
from django.test import TestCase

from portfolio.utils import get_image_path


class UtilsTests(TestCase):
    def test_get_image_path_no_sub_folder(self):
        file_name = 'test.jpg'
        store = storages['staticfiles']
        upload_folder = 'tests/'
        dt = datetime.today().strftime('%Y%m%d')

        expected_path = dt+'/test_{0}w.jpg'
        actual_path = get_image_path(file_name, store, upload_folder=upload_folder)

        self.assertEqual(expected_path, actual_path)

    def test_get_image_path_sub_folder(self):
        file_name = 'test.jpg'
        store = storages['staticfiles']
        upload_folder = 'tests/'
        sub_folder = 'sub_folder/'

        expected_path = 'sub_folder/test_{0}w.jpg'
        actual_path = get_image_path(file_name, store, sub_folder=sub_folder, upload_folder=upload_folder)

        self.assertEqual(expected_path, actual_path)

    def test_get_image_path_sub_folder_no_slash(self):
        file_name = 'test.jpg'
        store = storages['staticfiles']
        upload_folder = 'tests/'
        sub_folder = 'sub_folder'

        expected_path = 'sub_folder/test_{0}w.jpg'
        actual_path = get_image_path(file_name, store, sub_folder=sub_folder, upload_folder=upload_folder)

        self.assertEqual(expected_path, actual_path)