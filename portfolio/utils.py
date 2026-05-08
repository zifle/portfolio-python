import os
from datetime import datetime

from PIL import ImageOps, ExifTags
from PIL.ExifTags import TAGS
from PIL.Image import Exif
from PIL.ImageFile import ImageFile
from PIL.TiffImagePlugin import IFDRational
from django.core.files.storage import Storage


def resize_image(im: ImageFile, max_width=2000):
    """
    Resize the image, keeping its aspect ratio, to the desired width.
    Note that images may be taller than the max_width specified.
    """
    image = ImageOps.contain(im, (max_width, max_width * 3))
    return image

def get_image_path(filename:str, store:Storage, upload_folder='', sub_folder=None) -> str:
    """
    Get the image path to use for `filename`, within the `upload_folder`,
    and an optional `sub_folder`.
    Returns value `{sub_folder}/{filename}`, while creating folders for
    `STORE_PATH/{upload_folder}/{sub_folder}`.
    """

    # Strip the file type from the name, so we can append size suffix
    filename = '.'.join(filename.lower().split('.')[:-1])
    if sub_folder is None:
        sub_folder = datetime.today().strftime('%Y%m%d')
    if sub_folder and not sub_folder.endswith('/'):
        sub_folder += '/'

    if upload_folder and not upload_folder.endswith('/'):
        upload_folder = upload_folder+'/'
    os.makedirs(store.path(upload_folder + sub_folder), exist_ok=True)
    return f'{sub_folder}{filename}_{{0}}w.jpg'


def exif_to_dict(exif: Exif) -> dict[str, None|str|float|int]:
    gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
    exif_dict: dict[str, None | str | float | int] = {
        'gps_lat': None,
        'gps_lng': None,
    }
    if len(gps_info) > 0:
        # Fetch the GPS info, if available
        def decimal_coords(coords, ref):
            decimal_degrees = float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
            if ref == "S" or ref == 'W':
                decimal_degrees = -1 * decimal_degrees
            return decimal_degrees

        exif_dict['gps_lat'] = decimal_coords(gps_info[2], gps_info[1])
        exif_dict['gps_lng'] = decimal_coords(gps_info[4], gps_info[3])

    for k, v in exif.items():
        tag_name = TAGS.get(k, k)
        if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
            exif_dict[tag_name] = v

    # Get extra data from the EXIF IFD (includes things like lens model, etc.)
    exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    for k, v in exif_ifd.items():
        tag_name = TAGS.get(k, k)
        if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
            exif_dict[tag_name] = v
        elif isinstance(v, IFDRational):
            exif_dict[tag_name] = int(v.numerator) / v.denominator
            exif_dict[tag_name + '_repr'] = repr(v)

    return exif_dict