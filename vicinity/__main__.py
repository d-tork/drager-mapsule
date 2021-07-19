import os
from vicinity.bing import Geocoords
from vicinity.distance import VicinityCalculator
from vicinity import PROJ_PATH


def main():
    my_location = Geocoords(38.896593209560756, -77.02620469830747)
    vicinity_calc = VicinityCalculator(
        entity1='Shell gas station',
        entity2='sushi',
        my_location=my_location
    )
    vicinity_calc.get_results()
    distance_outfile = os.path.join(PROJ_PATH, 'data', 'distances.csv')
    vicinity_calc.distances.to_csv(distance_outfile, index_label='index')


if __name__ == '__main__':
    main()
