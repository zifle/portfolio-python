from django.test import TestCase

from portfolio.models import Location

def create_location(name:str, loc:str):
    lat, lng = loc.split(',')
    return Location.objects.create(name=name, coordinate_lat=float(lat), coordinate_lng=float(lng))

class LocationModelTests(TestCase):
    def test_get_mean_position(self):
        locs = [
            # Somewhere in the north sea
            (54.2438851,3.2337701),
            (54.2456971,3.2385771),
            (54.2455281,3.2358301),
        ]
        expected_lat = 54.245036766666665
        expected_lng = 3.2360591

        actual_lat, actual_lng = Location.get_mean_gps_position(locs)
        self.assertEqual(expected_lat, actual_lat)
        self.assertEqual(expected_lng, actual_lng)

    def test_nearby_locations(self):
        ra = create_location('Royal Arena', '55.625703316933354,12.573870488644037')
        vega = create_location('Vega', '55.668155198857725,12.543777489451566')
        poolen = create_location('Poolen', '55.69093346993234,12.622421822634852')
        copenhell = create_location('Copenhell', '55.69211200580459,12.617645676499615')
        kb = create_location('KB Hallen', '55.67800932414609,12.49494598711535')
        tivoli = create_location('Tivoli', '55.67368151443461,12.568250883570242')

        glyptotek = (55.673009514952525, 12.57253045902117)
        glyptotek_nearby_list = [
            tivoli,
            vega,
            copenhell,
            poolen,
            kb,
            ra
        ]
        glyptotek_nearby_dist = 0.2785556951585444

        result_glyptotek_nearby = Location.get_nearby([glyptotek])
        self.assertEqual(result_glyptotek_nearby[0].distance, glyptotek_nearby_dist)
        self.assertQuerySetEqual(glyptotek_nearby_list, Location.get_nearby([glyptotek]))