import os
from datetime import datetime
import io
import json

from PIL.Image import Exif
from PIL.ImageFile import ImageFile
from PIL.TiffImagePlugin import IFDRational
from django.core.files.storage import Storage, storages
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from PIL import Image, ExifTags, ImageOps
from PIL.ExifTags import TAGS

from portfolio.models import Album, Location, Camera, Lens, Category, Image as ImageModel
from portfolio.utils import get_mean_gps_position


# Create your views here.

def index_view(request, resource):
    return render(request, 'dist/index.html', {})

# ------------------------    Authentication    ------------------------
@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    """We set the CSRF cookie on the frontend"""
    return JsonResponse({"message": "CSRF cookie set"})

@require_http_methods(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        pw = data['password']
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    user = authenticate(request, username=username, password=pw)

    if user:
        login(request, user)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Invalid credentials"}, status=401)

def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out"})

@require_http_methods(['GET'])
def user(request):
    if request.user.is_authenticated:
        return JsonResponse({"username": request.user.username, "email": request.user.email})
    return JsonResponse({"message": "Not logged in"}, status=401)





# ------------------------    API Routes    ------------------------

class CategoryIndex(View):
    def get(self, request):
        cats = Category.objects.annotate(num_albums=Count('album'))
        cats_list = [cat.to_dict() for cat in cats]
        return JsonResponse(cats_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)
        data = json.loads(request.body.decode('utf-8'))
        if 'id' in data and data['id'] > 0:
            category = get_object_or_404(Category, pk=data['id'])
            category.name = data['name']
            category.order = data['order']
        else:
            category = Category.objects.create(name=data['name'], order=data['order'] or 0)
        category.save()

        data = category.to_dict()
        return JsonResponse(data)

class CategoryDetail(View):
    def delete(self, request, id):
        if not request.user.is_authenticated:
            return HttpResponse("Not logged in", status=401)
        category = get_object_or_404(Category, pk=id)
        category.delete()
        return HttpResponse("Deleted category", status=200)


class AlbumIndex(View):
    def get(self, request):
        if request.user.is_authenticated:
            albums = Album.objects.all()
        else:
            albums = Album.objects.filter(published=True)
        album_list = [album.to_dict() for album in albums]
        return JsonResponse(album_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        data = json.loads(request.body.decode('utf-8'))

        if 'category' in data and data['category'] is not None and data['category'] > 0:
            data['category'] = get_object_or_404(Category, pk=data['category'])
        else:
            data['category'] = None

        if 'location' in data and data['location'] is not None and data['location'] > 0:
            data['location'] = get_object_or_404(Location, pk=data['location'])
        else:
            data['location'] = None

        items = []
        if 'items' in data:
            items = data.pop('items')

        id = data.pop('id') if 'id' in data else 0

        if id and id > 0:
            album = get_object_or_404(Album, pk=id)
            for attr, value in data.items():
                setattr(album, attr, value)
        else:
            album = Album.objects.create(**data)

        album.save()
        album.set_album_items(items)

        data = album.to_dict()
        return JsonResponse(data)

class AlbumDetail(View):
    def get(self, request, id):
        album = None
        if isinstance(id, int):
            album = get_object_or_404(Album, pk=id)
        elif isinstance(id, str):
            album = get_object_or_404(Album, slug=id)
        if not album:
            return JsonResponse({'error': 'Album not found'}, status=404)
        data = album.to_dict()
        return JsonResponse(data, safe=False)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        album = get_object_or_404(Album, pk=id)
        if album.published:
            return JsonResponse({"message": "Published albums cannot be deleted"}, status=400)

        album.delete()
        return JsonResponse({"success": True})

class AlbumUpload(View):
    image_sizes = [
        300,
        500,
        800,
        1200,
        2000
    ]
    upload_folder = 'uploads/'

    def get(self, request, id):
        """Temporary test method for location suggestion code"""
        lat = 55.6897079
        lng = 12.6003911
        sLocations = Location.get_nearby([(lat, lng)])
        locations = [loc.to_dict() for loc in sLocations]
        return JsonResponse(locations, safe=False)

    def post(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        imglist: list[ImageModel] = []
        gps_coords = []
        for img in request.FILES:
            img_file = request.FILES[img]
            store = storages['staticfiles']
            img_model = ImageModel()
            try:
                with Image.open(io.BytesIO(img_file.read())) as im:
                    exif = im.getexif()
                    fname = self.get_image_path(img_file.name, store)
                    img_model.path = fname
                    exif_dict = self.img_exif_dict(exif)
                    self.set_exif_params(img_model, exif_dict)
                    duplicate = self.has_duplicate_image(img_model)
                    if duplicate:
                        del img_model
                        img_model = duplicate
                    else:
                        resizes = self.make_image_resizes(im, fname, store)
                        img_model.available_res = resizes['available_sizes']
                        img_model.max_width = resizes['max_width']
                        img_model.max_height = resizes['max_height']
            except OSError as e:
                return JsonResponse({"message": f"Uploaded file not an image!: {e}"}, status=400)

            img_model.save()
            imglist.append(img_model)
            if exif_dict['gps_lat'] and exif_dict['gps_lng']:
                gps_coords.append((exif_dict['gps_lat'], exif_dict['gps_lng']))

        locations = Location.get_nearby(gps_coords)
        cameras = {im.camera for im in imglist if im.camera is not None}
        lenses = {im.lens for im in imglist if im.lens is not None}
        locs = sorted([loc.to_dict() for loc in locations], key=lambda loc: loc['distance'])
        dates = set()
        for im in imglist:
            if im.date_taken:
                dates.add(im.date_taken.date())
            else:
                dates.add(None)

        return JsonResponse({
            "success": True,
            "cameras": [camera.to_dict() for camera in cameras],
            "lenses": [lens.to_dict() for lens in lenses],
            "images": [i.to_dict() for i in imglist],
            "locations": locs,
            "dates": sorted(list(dates)),
        })

    @staticmethod
    def img_exif_dict(exif: Exif) -> dict[str, None|str|float|int]:
        gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
        exifDict: dict[str, None|str|float|int] = {
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

            exifDict['gps_lat'] = decimal_coords(gps_info[2], gps_info[1])
            exifDict['gps_lng'] = decimal_coords(gps_info[4], gps_info[3])

        for k, v in exif.items():
            tag_name = TAGS.get(k, k)
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                exifDict[tag_name] = v

        # Get extra data from the EXIF IFD (includes things like lens model, etc.)
        exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        for k, v in exif_ifd.items():
            tag_name = TAGS.get(k, k)
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                exifDict[tag_name] = v
            elif isinstance(v, IFDRational):
                exifDict[tag_name] = int(v.numerator)/v.denominator
                exifDict[tag_name+'_repr'] = repr(v)

        return exifDict

    @staticmethod
    def resize_image(im: ImageFile, max_width=2000):
        """
        Resize the image, keeping its aspect ratio, to the desired width.
        Note that images may be taller than the max_width specified.
        """
        image = ImageOps.contain(im, (max_width, max_width*3))
        return image

    @classmethod
    def get_image_path(cls, filename:str, store:Storage):
        # Strip the file type from the name, so we can append size suffix
        filename = '.'.join(filename.lower().split('.')[:-1])
        date = datetime.today().strftime('%Y%m%d')
        upload_folder = cls.upload_folder
        os.makedirs(store.path(upload_folder + date), exist_ok=True)
        return f'{date}/{filename}_{{0}}w.jpg'

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
            if ExifTags.TAGS[orientation] == 'Orientation': break
        if exif[orientation] == 3:
            im = im.rotate(180, expand=True)
        elif exif[orientation] == 6:
            im = im.rotate(270, expand=True)
        elif exif[orientation] == 8:
            im = im.rotate(90, expand=True)

        upload_folder = cls.upload_folder
        for max_dimension in cls.image_sizes:
            img = cls.resize_image(im.copy(), max_dimension)
            if img.height > resizes['max_height']:
                resizes['max_height'] = img.height
            if img.width > resizes['max_width']:
                resizes['max_width'] = img.width
            _filename = fname.format(max_dimension)
            storePath = store.path(upload_folder + _filename)
            img.save(storePath)
        return resizes

    @staticmethod
    def set_exif_params(model: ImageModel, exif: dict[str, None|str|float|int]):
        if 'Make' in exif and 'Model' in exif:
            camera_brand = exif['Make']
            camera_model = exif['Model']
            camera, _ = Camera.objects.get_or_create(brand=camera_brand, model=camera_model)
            model.camera = camera

        if 'LensMake' in exif:
            lens_brand = str(exif['LensMake']).strip()
            lens_model = str(exif['LensModel']).strip(' \u0000')
            lens, _ = Lens.objects.get_or_create(brand=lens_brand, model=lens_model)
            model.lens = lens

        try:
            date_taken = None
            if 'DateTimeOriginal' in exif:
                date_taken = exif['DateTimeOriginal']
            elif 'DateTime' in exif:
                date_taken = exif['DateTime']
            elif 'DateTimeDigitized' in exif:
                date_taken = exif['DateTimeDigitized']

            if 'OffsetTimeOriginal' in exif:
                time_offset = exif['OffsetTimeOriginal']
            elif 'OffsetTime' in exif:
                time_offset = exif['OffsetTime']
            else:
                time_offset = '+0000'

            if date_taken:
                # Create a UTC Datetime from the two values
                dt = f'{date_taken} {time_offset.replace(':', '')}'
                date = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S %z')
                model.date_taken = date
        except KeyError:
            pass

        if 'FocalLength' in exif:
            model.focal_length = exif['FocalLength']

        if 'FocalLengthIn35mmFilm' in exif:
            model.focal_length_35 = exif['FocalLengthIn35mmFilm']

        if 'ExposureTime' in exif:
            model.exposure_time = f'1/{1/exif['ExposureTime']}'

        if 'ExposureBiasValue' in exif:
            model.exposure_compensation = exif['ExposureBiasValue']

        if 'FNumber' in exif:
            model.aperture = exif['FNumber']

    @staticmethod
    def has_duplicate_image(img: ImageModel) -> ImageModel|None:
        """
        Check the DB for a saved Image with the same filename and date_taken.
        If there's a match, it's most likely the same exact image being reuploaded,
        and we can simply return the existing image instance instead of handling it again.
        """
        path = img.path.split('/')[1]
        date_taken = img.date_taken
        try:
            existing = ImageModel.objects.get(date_taken=date_taken, path__endswith=path)
            return existing
        except ImageModel.DoesNotExist:
            pass
        except ImageModel.MultipleObjectsReturned:
            return ImageModel.objects.filter(date_taken=date_taken, path__endswith=path).first()
        return None

@ensure_csrf_cookie
@require_http_methods(['POST'])
def albumTogglePublish(request, id:int):
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in", status=401)
    album = get_object_or_404(Album, pk=id)
    data = json.loads(request.body.decode('utf-8'))
    if data['publish'] == True:
        album.published = True
    else:
        album.published = False
    album.save()
    return JsonResponse({"success": True})


class LocationsIndex(View):
    def get(self, request):
        locs = Location.objects.annotate(num_albums=Count('album'))
        locs_list = [loc.to_dict() for loc in locs]
        return JsonResponse(locs_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)
        data = json.loads(request.body.decode('utf-8'))
        if 'id' in data and data['id'] > 0:
            location = get_object_or_404(Location, pk=data['id'])
            location.name = data['name']
            location.coordinate_lat = data['coordinate_lat']
            location.coordinate_lng = data['coordinate_lng']
        else:
            location = Location.objects.create(
                name=data['name'],
                coordinate_lat=data['coordinate_lat'],
                coordinate_lng=data['coordinate_lng'],
            )
        location.save()

        data = model_to_dict(location)
        return JsonResponse(data)

def camerasIndex(request):
    return JsonResponse(list(Camera.objects.all()), safe=False)

def lensIndex(request):
    return JsonResponse(list(Lens.objects.all()), safe=False)

