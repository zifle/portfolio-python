from django.db import models
from django.forms import model_to_dict
from django.db.models import QuerySet, F
from django.db.models.functions import ACos, Cos, Radians, Sin

class Location(models.Model):
    class Meta:
        db_table = "locations"

    name = models.CharField(max_length=100, )
    coordinate_lng = models.FloatField(
        "longitudinal coordinates",
        null=True,
        blank=True,
    )
    coordinate_lat = models.FloatField(
        "latitudinal coordinates",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} <{self.coordinate_lat},{self.coordinate_lng}>'

    def to_dict(self) -> dict:
        data = model_to_dict(self)

        if hasattr(self, 'distance'):
            data['distance'] = self.distance
        if hasattr(self, 'num_albums'):
            data['num_albums'] = self.num_albums

        return data

    @classmethod
    def get_nearby(cls, gps_coords: list[tuple[float, float]]) -> QuerySet:
        """
        Given a list of (lat,long) tuples of coordinates, find an existing saved location
        within 1km of the point, and return the closest one (if multiple are found)
        """
        if len(gps_coords) == 0:
            return cls.objects.none()

        # SELECT
        #   name,
        #    ( 6371 * acos( cos( radians(57.046125) ) * cos( radians( locations.coordinate_lat ) )
        #    * cos( radians(locations.coordinate_lng) - radians(9.9310493)) + sin(radians(57.046125))
        #    * sin( radians(locations.coordinate_lat)))) AS distance
        # FROM locations
        # WHERE distance < 0.50
        # ORDER BY distance;
        max_distance_km = 10
        earth_radius_km = 6371
        pos_lat, pos_lng = cls.get_mean_gps_position(gps_coords)
        where = (earth_radius_km * ACos(Cos(Radians(pos_lat)) * Cos(Radians(F('coordinate_lat')))
                                        * Cos(Radians(F('coordinate_lng')) - Radians(pos_lng)) + Sin(Radians(pos_lat))
                                        * Sin(Radians(F('coordinate_lat')))))

        locations = cls.objects.annotate(distance=where).filter(distance__lte=max_distance_km)

        return locations

    @staticmethod
    def get_mean_gps_position(coords: list[tuple[float, float]]) -> tuple[float, float]:
        """
        Get the CENTROID position based on the input list.
        Note that we assume that the points are close enough to each other,
        that we treat the earth as locally flat, so simplify the calculation
        """
        if len(coords) == 0:
            raise ValueError
        lat = []
        long = []
        for l in coords:
            lat.append(l[0])
            long.append(l[1])

        mean_lat = sum(lat) / len(lat)
        mean_long = sum(long) / len(long)
        return mean_lat, mean_long