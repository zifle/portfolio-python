

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
