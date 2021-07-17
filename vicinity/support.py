"""Supporting classes and functions."""
from math import radians, cos, sin, asin, sqrt
from datetime import datetime as dt


class BadResponse(Exception):
    pass


def timing(f):
    def timed(*args, **kw):
        start = dt.now()
        print(f'Start: {start}')
        result = f(*args, **kw)
        finish = dt.now()
        print(f'Finish: {finish} ({finish-start})')
        return result
    return timed


def haversine(coords1, coords2):
    """ Get distance between two lat/lon pairs using the Haversine formula."""
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 3959.87433  # this is in miles. For kilometers use 6372.8 km

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    return R * c
