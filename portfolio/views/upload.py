from math import ceil
from multiprocessing import Pool, cpu_count
import time

from PIL.ImageFile import ImageFile
from django.core.files.storage import storages, Storage
from django.http import JsonResponse
from django.views import View
from PIL import Image as PILImage, ExifTags
import logging

from portfolio.models import Image, Location
from portfolio.utils import get_image_path, exif_to_dict, resize_image


class ImageUpload(View):
    image_sizes = [
        600,
        800,
        1200,
        1600,
        2000
    ]
    upload_folder = 'uploads/'

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        img_list: list[Image] = []
        gps_coords: list[tuple[float, float]] = []
        store: Storage = storages['staticfiles']
        logger = logging.getLogger('django')

        # Save temp files for handling in subprocesses
        save_tmp = time.time()
        handle_imgs = []
        for img in request.FILES:
            img_file = request.FILES[img]
            fname = store.save(img_file.name, img_file)
            handle_imgs.append(fname)
        logger.debug(f'Spent {time.time()-save_tmp}s saving tmp files')

        handle_time = time.time()
        handled_imgs = []
        
        # Local testing determined a negligable difference in using all (logical) cores,
        # vs just the physical (assumed to be 2 logical cores for each physical in standard
        # hyperthreading)
        physical_cores = max(1, ceil(cpu_count()/2))
        pool_size = min(physical_cores, len(request.FILES))
        if pool_size > 0:
            with Pool(pool_size) as pool:
                logger.debug(f'Starting process pool, with {pool_size} processes')
                maplist = [(filename, store) for filename in handle_imgs]
                handled_imgs = pool.starmap(self.handle_image_upload, maplist)
                logger.info(f'Spent {time.time()-handle_time}s handling uploaded files')
                logger.debug('Finished process pool, getting results')
                for img, gps in handled_imgs:
                    if img is not None:
                        img_list.append(img)
                    if gps is not None:
                        gps_coords.append(gps)

        locations = Location.get_nearby(gps_coords)
        cameras = {im.camera for im in img_list if im.camera is not None}
        lenses = {im.lens for im in img_list if im.lens is not None}
        locs = sorted([loc.to_dict() for loc in locations], key=lambda loc: loc['distance'])
        dates = set()
        for im in img_list:
            if im.date_taken:
                dates.add(im.date_taken.date())
            else:
                dates.add(None)

        return JsonResponse({
            "success": True,
            "cameras": [camera.to_dict() for camera in cameras],
            "lenses": [lens.to_dict() for lens in lenses],
            "images": [i.to_dict() for i in img_list],
            "locations": locs,
            "dates": sorted(list(dates)),
        })
    
    @classmethod
    def handle_image_upload(cls, filename, store:Storage) -> tuple[None|Image, None|tuple[float, float]]:
        img_model = Image()
        logger = logging.getLogger('django')
        logger.debug(f'Handling file {filename}')
        s = time.time()

        filepath = store.path(filename)
        try:
            with PILImage.open(filepath) as im:
                exif = im.getexif()
                file_save_path = get_image_path(filename, store, upload_folder=cls.upload_folder)
                img_model.path = file_save_path
                exif_dict = exif_to_dict(exif)
                img_model.set_exif_params(exif_dict)
                duplicate = img_model.has_duplicate()
                if duplicate:
                    del img_model
                    img_model = duplicate
                    im.close()
                else:
                    resizes = cls.make_image_resizes(im, file_save_path, store)
                    img_model.available_res = resizes['available_sizes']
                    img_model.max_width = resizes['max_width']
                    img_model.max_height = resizes['max_height']
            store.delete(filepath)
        except OSError as e:
            logger.error(e.strerror)
            return (None, None)

        img_model.save()
        rtn = (None, None)
        if isinstance(img_model, Image): # Check should be redundant, but IDE is complaining
            rtn = (img_model, None)
        if exif_dict['gps_lat'] and exif_dict['gps_lng']:
            rtn = (rtn[0], (exif_dict['gps_lat'], exif_dict['gps_lng']))

        logger.debug(f'Finished handling file {filename}')
        logger.info(f'Spent {time.time()-s}s handling {filename}')
        return rtn

    @classmethod
    def make_image_resizes(cls, im:ImageFile, fname:str, store:Storage) -> dict[str, str|int|list[int]]:
        logger = logging.getLogger('django')
        
        # fname = f'{date}/{filename}_{{0}}.jpg'
        resizes = {
            'path': fname,
            'available_sizes': cls.image_sizes,
            'max_width': 0,
            'max_height': 0,
        }

        # Get orientation, so we can properly rotate the image if it's not already been
        exif = im.getexif()
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                if orientation in exif:
                    if exif[orientation] == 3:
                        im = im.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        im = im.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        im = im.rotate(90, expand=True)
                break

        upload_folder = cls.upload_folder
        for max_dimension in cls.image_sizes:
            logger.debug(f'Resizing {fname} to {max_dimension}')
            img = resize_image(im.copy(), max_dimension)
            if img.height > resizes['max_height']:
                resizes['max_height'] = img.height
            if img.width > resizes['max_width']:
                resizes['max_width'] = img.width
            _filename = fname.format(max_dimension)
            storePath = store.path(upload_folder + _filename)
            img.save(storePath)
        return resizes