import pandas as pd
import geopandas as gpd

from os.path import join

geojson_dir = 'data/organized/spatial/'
variables_dir = 'data/organized'
years = ['40', '50', '60']

for y in years:
    g_in = join(geojson_dir, 'phila_{}.geojson'.format(y))
    g = gpd.read_file(g_in)
    d_in = join(variables_dir, 'variables_19{}.csv'.format(y))
    d = pd.read_csv(d_in)
    state = 'Geo_state'
    county = 'Geo_county'
    county_number = 101
    if y == '60':
        state = 'Geo_State'
        county = 'Geo_county60'
        county_number = 51
    d = d[(d[state] == 42) & (d[county] == county_number)]
    d = d[['Geo_QName', 'Geo_FIPS']]

    def e(s):
        s = s.split(',')[0].replace('Census Tract ', '')
        split = len(s)
        for i in range(0, len(s)):
            if not s[i].isdigit():
                split = i
                return str(int(s[:split])) + '-' + s[split:].replace('0', '')
        return s
    d['TRACTID'] = d['Geo_QName'].apply(e)
    gg = pd.merge(g, d[['Geo_FIPS', 'TRACTID']])
    g_out = g_in.replace('.geojson', '_with_fips.geojson')
    gg.to_file(driver='GeoJSON', filename=g_out)
