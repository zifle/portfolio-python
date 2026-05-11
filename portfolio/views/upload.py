import io

from PIL.ImageFile import ImageFile
from django.core.files.storage import storages, Storage
from django.http import JsonResponse
from django.views import View
from PIL import Image as PILImage, ExifTags

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
        gps_coords = []
        for img in request.FILES:
            img_file = request.FILES[img]
            store = storages['staticfiles']
            img_model = Image()
            try:
                with PILImage.open(io.BytesIO(img_file.read())) as im:
                    exif = im.getexif()
                    file_save_path = get_image_path(img_file.name, store, upload_folder=self.upload_folder)
                    img_model.path = file_save_path
                    exif_dict = exif_to_dict(exif)
                    img_model.set_exif_params(exif_dict)
                    duplicate = img_model.has_duplicate()
                    if duplicate:
                        del img_model
                        img_model = duplicate
                    else:
                        resizes = self.make_image_resizes(im, file_save_path, store)
                        img_model.available_res = resizes['available_sizes']
                        img_model.max_width = resizes['max_width']
                        img_model.max_height = resizes['max_height']
            except OSError as e:
                return JsonResponse({"message": f"Uploaded file not an image!: {e}"}, status=400)

            img_model.save()
            if isinstance(img_model, Image): # Check should be redundant, but IDE is complaining
                img_list.append(img_model)
            if exif_dict['gps_lat'] and exif_dict['gps_lng']:
                gps_coords.append((exif_dict['gps_lat'], exif_dict['gps_lng']))

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
    def make_image_resizes(cls, im:ImageFile, fname:str, store:Storage) -> dict[str, str|int|list[int]]:
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
                if exif[orientation] == 3:
                    im = im.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    im = im.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    im = im.rotate(90, expand=True)
                break

        upload_folder = cls.upload_folder
        for max_dimension in cls.image_sizes:
            img = resize_image(im.copy(), max_dimension)
            if img.height > resizes['max_height']:
                resizes['max_height'] = img.height
            if img.width > resizes['max_width']:
                resizes['max_width'] = img.width
            _filename = fname.format(max_dimension)
            storePath = store.path(upload_folder + _filename)
            img.save(storePath)
        return resizes