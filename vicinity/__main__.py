import os
import pandas as pd
from vicinity.bing import BingMapsAPI, BingBusinessAPICall, Geocoords


def main():
    bing_api = BingMapsAPI()
    my_location = Geocoords(38.896593209560756, -77.02620469830747)
    bank_api_call = BingBusinessAPICall(query_string='wells fargo', startcoords=my_location)
    bank_listings = bing_api.get_nearby_businesses(business_request=bank_api_call)
    bank_listings_df = get_dataframe_from_results(bank_listings)
    print(bank_listings_df.shape)
    print(bank_listings_df)
    outfile = 'bank_listings'
    outpath = os.path.join(os.path.expanduser('~'), 'Downloads', f'{outfile}.csv')
    bank_listings_df.to_csv(outpath, index=False)


def get_dataframe_from_results(results: list) -> pd.DataFrame:
    """Store API results in a dataframe."""
    df = pd.DataFrame.from_dict(results)
    df_with_coords_extracted = extract_lat_lon_from_point_col(df, colname='point')
    return df_with_coords_extracted


def extract_lat_lon_from_point_col(df, colname: str = 'point') -> pd.DataFrame:
    point_col = df[colname].map(eval)               # a column of type: dict
    point_coords_df = point_col.apply(pd.Series)    # a dataframe where coords col is lists
    geocoords_df = point_coords_df['coordinates'].apply(pd.Series)
    geocoords_df.columns = ['lat', 'lon']
    joined = df.join(geocoords_df)
    return joined


if __name__ == '__main__':
    main()