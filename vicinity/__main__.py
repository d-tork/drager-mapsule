import os
import pandas as pd
from vicinity.bing import BingMapsAPI, LocalSearchAPICall, Geocoords


def main():
    bing_api = BingMapsAPI()
    my_location = Geocoords(38.896593209560756, -77.02620469830747)
    bank_api_call = LocalSearchAPICall(query='wells fargo', startcoords=my_location, max_results=25)
    bank_listings = bing_api.get_local_search(local_search=bank_api_call)
    bank_listings_df = get_dataframe_from_results(bank_listings)
    print(bank_listings_df.shape)
    print(bank_listings_df)
    outfile = 'bank_listings'
    outpath = os.path.join(os.path.expanduser('~'), 'Downloads', f'{outfile}.csv')
    bank_listings_df.to_csv(outpath, index=False)


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
    joined = df.join(geocoords_df)
    return joined


def parse_address_as_string(df, colname: str = 'Address') -> pd.DataFrame:
    addr_col = df[colname]
    addr_df = addr_col.apply(pd.Series)
    joined = df.join(addr_df)
    return joined


if __name__ == '__main__':
    main()