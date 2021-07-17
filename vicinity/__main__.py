import os
from datetime import datetime
import pandas as pd
from vicinity.bing import BingMapsAPI, LocalSearchAPICall, Geocoords
from vicinity.support import haversine


def main():
    bing_api = BingMapsAPI()
    my_location = Geocoords(38.896593209560756, -77.02620469830747)
    entity_1 = get_results_for_entity('verizon', bing_api, my_location)
    entity_2 = get_results_for_entity('chipotle', bing_api, my_location)

    full = pd.concat([entity_1, entity_2])
    outfile = 'Veroxxotle'
    outpath = os.path.join(os.path.expanduser('~'), 'Downloads', f'{outfile}.csv')
    full.to_csv(outpath, index_label='index')

    distances = get_distances(entity_1['coordinates'], entity_2['coordinates'])
    distance_outfile = os.path.join(os.path.expanduser('~'), 'Downloads', 'distances.csv')
    distances_df = pd.DataFrame(distances)
    distances_df.to_csv(distance_outfile, index=False)


def get_results_for_entity(query: str, bing_api: BingMapsAPI, my_location: Geocoords) -> pd.DataFrame:
    """Search for map results for a given query."""
    local_search = LocalSearchAPICall(query=query, startcoords=my_location, max_results=25)
    local_results = bing_api.get_local_search(local_search=local_search)
    local_results_df = get_dataframe_from_results(local_results)
    timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    outfile = f'localsearch_{query}_{timestamp}'
    outpath = os.path.join(os.path.expanduser('~'), 'Downloads', f'{outfile}.csv')
    local_results_df.to_csv(outpath, index=False)
    cols_to_return = ['name', 'PhoneNumber', 'entityType', 'formattedAddress', 'coordinates', 'lat', 'lon']
    return local_results_df[cols_to_return]


def get_dataframe_from_results(results: list) -> pd.DataFrame:
    """Store API results in a dataframe."""
    df = pd.DataFrame.from_dict(results)
    df = extract_lat_lon_from_point_col(df, colname='point')
    df = parse_address_as_string(df, colname='Address')
    return df


def extract_lat_lon_from_point_col(df, colname: str = 'point') -> pd.DataFrame:
    point_col = df[colname]
    point_coords_df = point_col.apply(pd.Series)    # a dataframe where coords col is lists
    geocoords_df = point_coords_df['coordinates'].apply(pd.Series)
    geocoords_df.columns = ['lat', 'lon']
    joined = df.join(point_coords_df).join(geocoords_df)
    return joined


def parse_address_as_string(df, colname: str = 'Address') -> pd.DataFrame:
    addr_col = df[colname]
    addr_df = addr_col.apply(pd.Series)
    joined = df.join(addr_df)
    return joined


def get_distances(s1, s2):
    pairs = []
    for i1, coords1 in s1.iteritems():
        for i2, coords2 in s2.iteritems():
            dist = haversine(coords1, coords2)
            dist_tuple = (i1, i2, dist)
            pairs.append(dist_tuple)
    return pairs


if __name__ == '__main__':
    main()