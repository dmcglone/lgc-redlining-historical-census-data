import os
import argparse
import geopandas as gpd
import pandas as pd
from os.path import join

from utils import tract_code_to_fips


class StudyAreaTracts():

    def __init__(self, tracts2010):
        tracts = gpd.read_file(tracts2010)[
            ['STATE', 'COUNTY', 'TRACT', 'geometry']]
        tracts['Geo_FIPS'] = tracts['STATE'].str.cat(
            [tracts['COUNTY'], tracts['TRACT']])
        self.tracts = tracts
        self.poly = tracts.geometry
        self.legacy_tracts = {}

    def add_legacy_tracts(self, legacy_tracts, year):
        lt = gpd.read_file(legacy_tracts)
        lt['geometry'] = lt.centroid
        tract_var = 'Geo_FIPS_' + year
        lt[tract_var] = lt['TRACTID'].apply(tract_code_to_fips)
        lt = lt[[tract_var, 'geometry']]
        self.legacy_tracts[year] = lt
        joined = gpd.sjoin(self.tracts, lt, how='left')
        self.tracts = joined.drop('index_right', axis=1)


def lookup_tables(contemporary_tracts, legacy_tracts_dir, neighborhood_input,
                  output_file):
    sat = StudyAreaTracts(contemporary_tracts)
    for i in ['40', '50', '60']:
        yr = '19' + i
        f = 'phila_{}.geojson'.format(i)
        sat.add_legacy_tracts(join(legacy_tracts_dir, f), yr)
    centroids = sat.tracts
    centroids.geometry = centroids.centroid
    neighborhoods = gpd.read_file(neighborhood_input)
    joined = gpd.sjoin(centroids, neighborhoods, how='left')
    sat.tracts['Neighborhood'] = joined['NAME']

    # write a csv lookup table to match historical tracts/neighborhoods
    # to 2010 tracts
    if os.path.isfile(output_file):
        os.remove(output_file)
    df = pd.DataFrame(sat.tracts).drop('geometry', axis=1)
    df.to_csv(output_file, index=False)

    # write a geojson with Geo_FIPS field
    sat.tracts.geometry = sat.poly
    sat.tracts = sat.tracts.groupby(['Geo_FIPS']).first().reset_index()[
        ['Geo_FIPS', 'geometry']]
    sat.tracts = gpd.GeoDataFrame(sat.tracts)
    geojson_output = output_file.replace('.csv', '.geojson')
    if os.path.isfile(geojson_output):
        os.remove(geojson_output)
    sat.tracts.to_file(driver='GeoJSON', filename=geojson_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Join legacy census tracts to contemporary')
    parser.add_argument('contemporary_tracts')
    parser.add_argument('legacy_tracts_dir')
    parser.add_argument('neighborhoods')
    parser.add_argument('output_file')
    args = parser.parse_args()
    lookup_tables(args.contemporary_tracts, args.legacy_tracts_dir,
                  args.neighborhoods, args.output_file)
