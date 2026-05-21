import io
from math import ceil
from multiprocessing import Pool, cpu_count
import time
import json
from datetime import datetime

from PIL.ImageFile import ImageFile
from django.core.files.storage import storages, Storage
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse, HttpRequest
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
    # todo Move these props to env or settings for global use
    upload_folder = 'uploads/'
    use_store = 'staticfiles'

    def post(self, request:HttpRequest):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        gps_coords: list[tuple[float, float]] = []
        logger = logging.getLogger('django')

        if len(request.FILES) > 1:
            img_list: list[Image] = []
            store: Storage = storages[self.use_store]

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
                    handled_imgs = pool.map(self.handle_image_upload, handle_imgs)
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
            locs = [loc.to_dict() for loc in locations]
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
        elif len(request.FILES) == 1:
            im = None
            gps = None
            for img in request.FILES:
                logger.debug(f'Found file {img} in request')
                img_file = request.FILES[img]
                im, gps = self.handle_image_upload(img_file)
                break

            if im is None:
                return JsonResponse({"message": "Image file not in request"}, status=400)
            
            if gps is not None:
                gps_coords.append(gps)

            return JsonResponse({
                "success": True,
                "cameras": [im.camera.to_dict()],
                "lenses": [im.lens.to_dict()],
                "images": [im.to_dict()],
                "coords": gps_coords,
                "date": im.date_taken.date() if im.date_taken else None,
            })
    
    @classmethod
    def handle_image_upload(cls, filename:str|UploadedFile) -> tuple[None|Image, None|tuple[float, float]]:
        img_model = Image()
        store: Storage = storages[cls.use_store]
        logger = logging.getLogger('django')
        logger.debug(f'Handling file {filename if isinstance(filename, str) else filename.name}')
        s = time.time()

        deleteTmpFile = False
        if isinstance(filename, str):
            filepath = store.path(filename)
            deleteTmpFile = True
        elif isinstance(filename, UploadedFile):
            filepath = io.BytesIO(filename.read())
            filename = filename.name
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
                else:
                    resizes = cls.make_image_resizes(im, file_save_path, store)
                    img_model.available_res = resizes['available_sizes']
                    img_model.max_width = resizes['max_width']
                    img_model.max_height = resizes['max_height']
                    img_model.save()
            
            if deleteTmpFile:
                store.delete(filepath)
        except OSError as e:
            logger.error(e.strerror)
            return (None, None)

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
    
class CheckDuplicates(View):
    # todo Move these props to env or settings for global use
    upload_folder = 'uploads/'
    use_store = 'staticfiles'

    def post(self, request:HttpRequest):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)
        
        store: Storage = storages[self.use_store]

        data = json.loads(request.body.decode('utf-8'))

        locations: list[tuple[float, float]] = []

        img_list = []
        dates = set()
        to_upload = []
        for i in data:
            img_model = Image()
            filename = i["filename"]
            file_save_path = get_image_path(filename, store, upload_folder=self.upload_folder)
            img_model.path = file_save_path
            img_model.date_taken = datetime.fromisoformat(i["date_taken"])
            dates.add(img_model.date_taken.date())
            
            duplicate: Image|None = img_model.has_duplicate()
            if duplicate:
                img_list.append(duplicate)
            else:
                to_upload.append(filename)

            if "location" in i and i["location"] is not None:
                lat = i["location"][0]
                lng = i["location"][1]
                locations.append((lat, lng))
        
        locs = Location.get_nearby(locations)
        cameras = {im.camera for im in img_list if im.camera is not None}
        lenses = {im.lens for im in img_list if im.lens is not None}

        return JsonResponse({
            "success": True,
            "cameras": [camera.to_dict() for camera in cameras],
            "lenses": [lens.to_dict() for lens in lenses],
            "images": [i.to_dict() for i in img_list],
            "locations": [loc.to_dict() for loc in locs],
            "dates": sorted(list(dates)),
            "upload": to_upload,
        })
