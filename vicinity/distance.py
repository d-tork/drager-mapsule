"""Perform distance calculations and dataframe operations."""
import os
import pandas as pd
from datetime import datetime
from vicinity.bing import BingMapsAPI, LocalSearchAPICall, Geocoords
from vicinity.support import haversine
from vicinity import PROJ_PATH


class VicinityCalculator(object):
    """
    Calculates distances between all local instances of specified map entities.

    """
    def __init__(self, entity1, entity2, my_location):
        """Instantiate a vicinity calculator.

        Args:
            entity1, entity2 (str): queries for Bing Maps LocalSearch for locations of interest
            my_location (array-like): a pair of floats for lat and lon, focusing the search
                results.
        """
        self.bing_api = BingMapsAPI()
        self.entity1 = entity1
        self.entity2 = entity2
        self.my_location = my_location
        self.distances = pd.DataFrame()

    def get_results(self):
        """Fetch map results for both entities and calculate distances."""
        entity1_data = self._get_results_for_entity(query=self.entity1)
        entity2_data = self._get_results_for_entity(query=self.entity2)
        raw_distances = get_distances(entity1_data['coordinates'], entity2_data['coordinates'])
        self.distances = (
            pd.DataFrame(raw_distances, columns=['entity1', 'entity2', 'distance'])
                .sort_values('distance')
                .reset_index(drop=True)
                          )

    def _get_results_for_entity(self, query: str) -> pd.DataFrame:
        """Search for map results for a given query."""
        local_search = LocalSearchAPICall(query=query, startcoords=self.my_location, max_results=25)
        local_results = self.bing_api.get_local_search(local_search=local_search)
        local_results_df = self._get_dataframe_from_results(local_results)

        # Set index to a meaningful identifer for each row
        local_results_df = local_results_df.assign(
            index_col=local_results_df['name'] + ' - ' + local_results_df['addressLine']
        ).set_index('index_col')

        timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
        outfile = f'localsearch_{query}_{timestamp}'
        outpath = os.path.join(PROJ_PATH, 'data', f'{outfile}.csv')
        local_results_df.to_csv(outpath, index=False)
        cols_to_return = ['name', 'PhoneNumber', 'entityType', 'formattedAddress', 'coordinates', 'lat', 'lon']
        return local_results_df[cols_to_return]

    @staticmethod
    def _get_dataframe_from_results(results: list) -> pd.DataFrame:
        """Store API results in a dataframe."""
        df = pd.DataFrame.from_dict(results)
        df = extract_lat_lon_from_point_col(df, colname='point')
        df = parse_address_as_string(df, colname='Address')
        return df


def get_distances(s1: pd.Series, s2: pd.Series) -> list:
    """Join pairs of coordinates in two lists and compute their straight-line distances.

    Args:
        s1, s2: Pandas Series where each value is an array of (lat, lon). For maximum
            benefit, the index of each series should be a meaningful descriptor of that
            specific location.

    Returns: list of tuples of the form (index1, index2, distance_between_them)

    """
    pairs = []
    for i1, coords1 in s1.iteritems():
        for i2, coords2 in s2.iteritems():
            dist = haversine(coords1, coords2)
            dist_tuple = (i1, i2, dist)
            pairs.append(dist_tuple)
    return pairs


def extract_lat_lon_from_point_col(df, colname: str = 'point') -> pd.DataFrame:
    """Split lat and lon into separate columns if contained in a column of point arrays.

    Useful if a way to vectorize the calculation is found and is easier done with pure
    numeric columns.
    """
    point_col = df[colname]
    point_coords_df = point_col.apply(pd.Series)
    geocoords_df = point_coords_df['coordinates'].apply(pd.Series)
    geocoords_df.columns = ['lat', 'lon']
    joined = df.join(point_coords_df).join(geocoords_df)
    return joined


def parse_address_as_string(df, colname: str = 'Address') -> pd.DataFrame:
    addr_col = df[colname]
    addr_df = addr_col.apply(pd.Series)
    joined = df.join(addr_df)
    return joined
