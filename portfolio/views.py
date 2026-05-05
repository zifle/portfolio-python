import os
from datetime import datetime
import io
import json

from PIL.Image import Exif
from PIL.ImageFile import ImageFile
from PIL.TiffImagePlugin import IFDRational
from django.core.files.storage import Storage, storages
from django.db.models import Count, F, Q
from django.db.models.functions import ACos, Cos, Radians, Sin
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
        cats_list = []
        for cat in cats:
            cDict = model_to_dict(cat)
            cDict['num_albums'] = cat.num_albums
            cats_list.append(cDict)
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

        data = model_to_dict(category)
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
        albums = Album.objects.annotate(num_images=Count('albumitems'))
        album_list = []
        for album in albums:
            aDict = model_to_dict(album)
            aDict['num_images'] = album.num_images
            album_list.append(aDict)
        return JsonResponse(album_list, safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not logged in"}, status=401)

        data = json.loads(request.body.decode('utf-8'))
        if 'id' in data and data['id'] > 0:
            album = get_object_or_404(Album, pk=data['id'])

            if 'category' in data and data['category'] is not None and data['category'] > 0:
                album.category = get_object_or_404(Category, pk=data['category'])
            else:
                album.category = None

            if 'location' in data and data['location'] is not None and data['location'] > 0:
                album.location = get_object_or_404(Location, pk=data['location'])
            else:
                album.location = None
            pass
        else:
            album = Album.objects.create(title=data['title'], description=data['description'])
            pass
        album.save()

        data = model_to_dict(album)
        return JsonResponse(data)

class AlbumDetail(View):
    def get(self, request, id):
        album = get_object_or_404(Album, pk=id)
        data = model_to_dict(album)
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

    def get(self, request, id):
        """Temporary test method for location suggestion code"""
        lat = 55.6897079
        lng = 12.6003911
        return HttpResponse(str(self.get_location_suggestion([(lat,lng)])))

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
                    fname = self.get_image_path(im, img_file.name, store)
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
            except OSError as e:
                return JsonResponse({"message": f"Uploaded file not an image!: {e}"}, status=400)

            img_model.save()
            imglist.append(img_model)
            if exif_dict['gps_lat'] and exif_dict['gps_lng']:
                gps_coords.append((exif_dict['gps_lat'], exif_dict['gps_lng']))

        location = self.get_location_suggestion(gps_coords)
        cameras = {im.camera for im in imglist if im.camera is not None}
        lenses = {im.lens for im in imglist if im.lens is not None}

        return JsonResponse({
            "success": True,
            "cameras": list([model_to_dict(camera) for camera in cameras]),
            "lenses": list([model_to_dict(lens) for lens in lenses]),
            "images": [i.pk for i in imglist],
            "location": location,
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
    def resize_image(im: ImageFile, max_dimension=2000):
        image = ImageOps.contain(im, (max_dimension, max_dimension))
        return image

    @staticmethod
    def get_image_path(im:ImageFile, filename:str, store:Storage):
        # Strip the file type from the name, so we can append size suffix
        filename = '.'.join(filename.lower().split('.')[:-1])
        date = datetime.today().strftime('%Y%m%d')
        os.makedirs(store.path(date), exist_ok=True)
        return f'{date}/{filename}_{{0}}.jpg'

    @classmethod
    def make_image_resizes(cls, im:ImageFile, fname:str, store:Storage) -> dict[str, str|list[int]]:
        # fname = f'{date}/{filename}_{{0}}.jpg'
        resizes = {
            'path': fname,
            'available_sizes': cls.image_sizes
        }
        for max_dimension in cls.image_sizes:
            img = cls.resize_image(im.copy(), max_dimension)
            _filename = fname.format(max_dimension)
            storePath = store.path(_filename)
            img.save(storePath)
        return resizes

    @staticmethod
    def set_exif_params(model: ImageModel, exif: dict[str, None|str|float|int]):
        camera_brand = exif['Make']
        camera_model = exif['Model']
        camera, _ = Camera.objects.get_or_create(brand=camera_brand, model=camera_model)
        model.camera = camera

        if 'LensMake' in exif:
            lens_brand = str(exif['LensMake']).strip()
            lens_model = str(exif['LensModel']).strip()
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
    def get_location_suggestion(gps_coords: list[tuple[float, float]]) -> Location|None:
        """
        Given a list of (lat,long) tuples of coordinates, find an existing saved location
        within 1km of the point, and return the closest one (if multiple are found)
        """
        if len(gps_coords) == 0:
            return None

        # SELECT
        #   name,
        #    ( 6371 * acos( cos( radians(57.046125) ) * cos( radians( locations.coordinate_lat ) )
        #    * cos( radians(locations.coordinate_lng) - radians(9.9310493)) + sin(radians(57.046125))
        #    * sin( radians(locations.coordinate_lat)))) AS distance
        # FROM locations
        # WHERE distance < 0.50
        # ORDER BY distance;
        max_distance_km = 1
        earth_radius_km = 6371
        pos_lat, pos_lng = get_mean_gps_position(gps_coords)
        where = ( earth_radius_km * ACos( Cos( Radians( pos_lat ) ) * Cos( Radians( F('coordinate_lat') ))
           * Cos( Radians( F('coordinate_lng') ) - Radians(pos_lng)) + Sin(Radians(pos_lat))
           * Sin( Radians( F('coordinate_lat') ))))

        locations = Location.objects.annotate(distance=where).filter(distance__lte=max_distance_km)

        return locations.first()

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
        locs_list = []
        for loc in locs:
            lDict = model_to_dict(loc)
            lDict['num_albums'] = loc.num_albums
            locs_list.append(lDict)
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

