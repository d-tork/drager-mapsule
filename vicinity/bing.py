"""
Get coordinate lists from Bing Maps.
"""

import requests
import datetime as dt
import logging
from collections import namedtuple

from vicinity import keys
from vicinity import support

logger = logging.getLogger(__name__)


class BingFailure(Exception):
    pass


class BingMapsAPI(object):
    """Container for getting data from Bing Maps REST API."""

    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{type(self).__name__}')
        self.bingMapsKey = keys['bingMapsKey']

    def get_local_search(self, local_search) -> list:
        """Get results of a query near a specified location.

        Args:
            local_search (LocalSearchAPICall): URL constructor for this API call, containing
                the start coordinates.

        Returns:
            Array of query results.

        Raises:
            KeyError: If JSON from Bing does not match expected structure.

        """
        api_response = self._get_api_response(local_search)
        results = api_response['resourceSets'][0]['resources']
        return results

    def get_geocoords(self, geocoder):
        """Geocode a location with the route coordinates of a street address.

        Args:
            geocoder (BingGeocoderAPICall): URL constructor for this API call, containing
                the address to be geocoded.

        Returns:
            Geocoords: latitude and longitude as floats

        """
        api_response = self._get_api_response(geocoder)
        coordinates_value = (api_response.get('resourceSets')[0]
                             .get('resources')[0]
                             .get('geocodePoints')[-1]
                             .get('coordinates'))
        return Geocoords._make(coordinates_value)

    def get_walk_time(self, walk_request):
        """Retrieves the walking distance and duration between two sets of coords.

        Args:
            walk_request (BingWalkAPICall): URL constructor for this API call, containing
                the start and end coordinates.

        Returns:
            namedtuple:
                distance (float): Walk distance to destination in miles
                duration (int): Walk time to destination

        """
        api_response = self._get_api_response(walk_request)
        distance = api_response['resourceSets'][0]['resources'][0]['travelDistance']
        duration = api_response['resourceSets'][0]['resources'][0]['travelDuration']
        Walk = namedtuple('Walk', 'distance duration')
        walk = Walk(
            distance=round(distance, 2),
            duration='{}'.format(str(dt.timedelta(seconds=duration)))
        )
        return walk

    def _get_api_response(self, api_call) -> dict:
        """Sends HTTP request built from url and parameters.

        Args:
            api_call (BingAPICall): Baseurl and parameters.

        Raises:
            support.BadResponse: If Bing does not send back 200 response.

        """
        api_call.url_args['key'] = self.bingMapsKey
        response = requests.get(api_call.baseurl, params=api_call.url_args)
        if response.status_code != 200:
            raise support.BadResponse('Response code from bing not 200.')
        return response.json()


class Geocoords(namedtuple('Coordinates', 'lat lon')):
    """Latitude and longitude for a location on earth."""
    __slots__ = ()

    def to_string(self):
        """For passing to the Bing REST API"""
        return f'{self.lat},{self.lon}'


class BingAPICall(object):
    """Abstract class for constructing HTTP API calls."""
    __slots__ = ('baseurl', 'url_args')


class LocalSearchAPICall(BingAPICall):
    """Constructs URL args for API call to Bing maps for nearby businesses from query string

    Attributes:
        baseurl (str): URL for this Bing Maps API call.
        url_args (dict): Parameters to be appended to the `baseurl`.

    Args:
        query: information about the entities you are looking for
        max_results: maximum number of results to return. Optional, capped at 25.
        startcoords: a namedtuple of geographic coordinates (lat/lon) as integers. Optional.

    """
    baseurl = r"http://dev.virtualearth.net/REST/V1/LocalSearch/"

    def __init__(self, query: str, max_results: int = 25, startcoords: Geocoords = None):
        if startcoords:
            user_location = startcoords.to_string()
        else:
            user_location = startcoords
        url_args = {
            'query': query,
            'userLocation': user_location,
            'maxResults': min(max_results, 25),
            'key': None,  # added by BingMapAPI method
        }
        self.url_args = {k: v for k, v in url_args.items() if v is not None}


class BingGeocoderAPICall(BingAPICall):
    """Constructs URL args for API call to Bing maps for geocoding a street address.

    Attributes:
        baseurl (str): URL for this Bing Maps API call.
        url_args (dict): Parameters to be appended to the `baseurl`.

    Args:
        address: Mailing address.
        zip_code (Optional): Helps with accuracy of results. Defaults to None.
        user_location (Optional): Helps with accuracy of results. Defaults to None.

    """
    baseurl = r"http://dev.virtualearth.net/REST/v1/Locations"

    def __init__(self, address: str, zip_code: int = None, user_location: Geocoords = None):
        if user_location:
            user_location = user_location.to_string()
        url_args = {
            'countryRegion': 'US',
            'postalCode': zip_code,
            'addressLine': address,
            'inclnb': '1',
            'maxResults': '1',
            'key': None,  # added by BingMapAPI method
            'userLocation': user_location
        }
        self.url_args = {k: v for k, v in url_args.items() if v is not None}


class BingWalkAPICall(BingAPICall):
    """Constructs URL args for API call to Bing maps for walk time between two locations.

    Attributes:
        baseurl (str): URL for this Bing Maps API call.
        url_args (dict): Parameters to be appended to the `baseurl`.

    Args:
        startcoords (Geocoords): a namedtuple of geographic coordinates (lat/lon) as integers
        endcoords (Geocoords): same as startcoords

    """
    baseurl = r"http://dev.virtualearth.net/REST/V1/Routes/Walking"

    def __init__(self, startcoords, endcoords):
        url_args = {
            'wp.0': startcoords.to_string(),
            'wp.1': endcoords.to_string(),
            'optimize': 'time',
            'distanceUnit': 'mi',
            'key': None,  # added by BingMapAPI method
        }
        self.url_args = {k: v for k, v in url_args.items() if v is not None}
