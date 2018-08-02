import os
import geopandas as gpd
import pandas as pd
import numpy as np
import argparse
from shapely.geometry import Point
from numpy.random import RandomState, uniform
from shapely.geometry import shape

# Adapted from Andrew Gaidus' blog post: "Visualizing Population Distributions with Dot Density Maps" 
# http://andrewgaidus.com/Dot_Density_County_Maps/

ALL_RACES = ['as', 'bl', 'hi', 'mr', 'na', 'nh', 'or', 'wh']

def gen_random_points_poly(poly, num_points, seed = None):
    """
    Returns a list of N randomly generated points within a polygon. 
    """
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    i=0
    while len(points) < num_points:
        s=RandomState(seed+i) if seed else RandomState(seed)
        random_point = Point([s.uniform(min_x, max_x), s.uniform(min_y, max_y)])
        if random_point.within(poly):
            points.append(random_point)
        i+=1
    return points


def gen_points_in_gdf_polys(geometry, values, points_per_value = None, seed = None):
    """
    Take a GeoSeries of Polygens along with a Series of values and returns randomly generated points within
    these polygons. Optionally takes a "points_per_value" integer which indicates the number of points that 
    should be generated for each 1 value.
    """
    if points_per_value:
        new_values = (values/points_per_value).astype(int)
    else:
        new_values = values
    new_values = new_values[new_values>0]
    g = gpd.GeoDataFrame(data = {'vals':new_values}, geometry = geometry)
    
    a = g.apply(lambda row: tuple(gen_random_points_poly(row['geometry'], row['vals'], seed)), 1)
    b = gpd.GeoSeries(a.apply(pd.Series).stack(), crs = geometry.crs)
    b.name='geometry'
    return b


def gen_points_gdf_one_race(polygon_uri, year, points_per_value=None, seed=None):
    """
    Generate a geodataframe of points for one race
    """
    polygon_gdf = gpd.read_file(polygon_uri)
    
    polygon_file_name = os.path.basename(polygon_uri)
    
    race_var = polygon_file_name.split('tracts_t_p_')[1].split('.')[0]
    
    geom_series = polygon_gdf.geometry
    
    var_series = polygon_gdf['t_p_{}_{}'.format(race_var, year)]
    point_series = gen_points_in_gdf_polys(geom_series, var_series, points_per_value, seed)
    point_gdf = gpd.GeoDataFrame(point_series)
    point_gdf['race'] = race_var
    return point_gdf


def gen_points_gdf_all_races(polygons_dir_uri, year, points_per_value = None, races = ALL_RACES):
    """
    Combine point geodataframes for all races into one
    """
    seed = 1
    gdfs = []
    for race in races:
        polygon_geojson = 'tracts_t_p_{}.geojson'.format(race)
        polygon_uri = os.path.join(polygons_dir_uri, polygon_geojson)
        points = gen_points_gdf_one_race(polygon_uri, year, points_per_value, seed = seed)
        gdfs.append(points)
        seed *= 10
    gdfs = pd.concat(gdfs).reset_index()[['race', 'geometry']]
    return gdfs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate population dot density layer')
    parser.add_argument('polygons_dir_uri')
    parser.add_argument('year')
    parser.add_argument('points_per_value')
    parser.add_argument('geojson_output_file')
    args = parser.parse_args()
    gdf = gen_points_gdf_all_races(args.polygons_dir_uri, args.year, int(args.points_per_value))
    gdf.to_file(driver="GeoJSON", filename=args.geojson_output_file)


