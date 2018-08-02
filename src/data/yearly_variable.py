"""
Create a geojson with yearly values for a specified census variable
"""

import os
import argparse

import numpy as np
import geopandas as gpd
import pandas as pd


def main(variable):

    YEARS = list(map(lambda x: str(x), np.arange(1940, 2020, 10)))
    tabular_data_dir = "data/interim/"
    tracts_2010 = gpd.read_file(
        'data/organized/spatial/study_area_2010.geojson')
    tracts_2010['Geo_FIPS_2010'] = tracts_2010.GEO_ID.apply(
        lambda x: x.split('US')[1])

    for y in reversed(YEARS):
        if int(y) > 1960:
            f = os.path.join(tabular_data_dir, 'census_data_{}.csv'.format(y))
            tab_data_year = pd.read_csv(f)
            tab_data_year['Geo_FIPS_data'] = tab_data_year[
                'Geo_FIPS'].astype(str)
            try:
                tab_data_year = tab_data_year[['Geo_FIPS_data', variable]]
            except KeyError:
                print('Measurement field not found in data table for year {}.'.format(y))
            tab_data_year = tab_data_year.rename(
                index=str, columns={variable: variable + '_' + y})
            tracts_2010 = pd.merge(
                tracts_2010, tab_data_year,
                left_on='Geo_FIPS_2010', right_on='Geo_FIPS_data', how='left')
            if 'Geo_FIPS_data' in tracts_2010.columns:
                tracts_2010 = tracts_2010.drop(['Geo_FIPS_data'], 1)
            print('Merged data from year {}.'.format(y))
        else:
            f = 'data/organized/spatial/phila_{}_fields.geojson'.format(y[2:])
            tracts_historic = gpd.read_file(f)
            field = 'census_data_{}_{}'.format(y, variable)
            try:
                if len(tracts_historic[tracts_historic[field].apply(str) != '']) == 0:
                    print('{} not available for year {}.'.format(variable, y))
                else:
                    if field not in tracts_historic.columns:
                        print(
                            'Measurement field not found in data table for year {}.'.format(y))
                    else:
                        tracts_historic['Geo_FIPS_historic'] = tracts_historic[
                            'Geo_FIPS'].astype(str)
                        areas_historic = dict(
                            zip(tracts_historic['Geo_FIPS_historic'], tracts_historic['geometry'].area))
                        union = gpd.overlay(
                            tracts_2010, tracts_historic, how='union')
                        union = union[(union['Geo_FIPS_2010'].notnull()) & (
                            union['Geo_FIPS'].str.startswith('42101'))]
                        p = {}
                        for k, v in union.iterrows():
                            if v['Geo_FIPS_historic'] in areas_historic.keys():
                                prop_value = v['geometry'].area / \
                                    areas_historic[v['Geo_FIPS_historic']]
                                prop_key = (v['Geo_FIPS_2010'], v[
                                    'Geo_FIPS_historic'])
                                p[prop_key] = prop_value
                        u = pd.DataFrame(
                            union)[['Geo_FIPS_2010', 'Geo_FIPS_historic', field]]
                        u = u[u[field].apply(str) != '']
                        if variable.startswith('t'):

                            def _get_prop(x):
                                if not x[2]:
                                    return 0
                                else:
                                    return p[(x[0], x[1])] * int(x[2])

                            u['value'] = u.apply(_get_prop, 1)
                            u = u[['Geo_FIPS_2010', 'value']]
                            g = u.groupby(['Geo_FIPS_2010']
                                          ).sum().reset_index()
                            g.columns = ['Geo_FIPS_2010', variable + '_' + y]
                            tracts_2010 = pd.merge(tracts_2010, g)
                            print('Merged data from year {}.'.format(y))
                        else:
                            # TODO: more robust method for calculating average
                            # variables
                            u['value'] = u.apply(lambda x: int(x[2]), 1)
                            u = u[['Geo_FIPS_2010', 'value']]
                            g = u.groupby(['Geo_FIPS_2010']
                                          ).mean().reset_index()
                            g.columns = ['Geo_FIPS_2010', variable + '_' + y]
                            tracts_2010 = pd.merge(tracts_2010, g)
                            print('Merged data from year {}.'.format(y))
            except KeyError:
                print('{} not available for year {}.'.format(variable, y))

    tracts_2010 = tracts_2010[tracts_2010['COUNTY'] == '101']
    tract_output = os.path.join(
        'data/processed', 'tracts_' + variable + '.geojson')
    if os.path.isfile(tract_output):
        os.remove(tract_output)
    tracts_2010.to_file(driver="GeoJSON", filename=tract_output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Aggregate census tracts to historical neighborhoods')
    parser.add_argument('variable')
    args = parser.parse_args()
    main(args.variable)
