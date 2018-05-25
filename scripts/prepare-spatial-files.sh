#!/bin/bash

# first argument - directory with raw data
input_dir=$1

# second argument - directory with organized spatial data
spatial_dir=$2

#filter nj counties
ogr2ogr -f GeoJSON -overwrite -sql \
	"SELECT * FROM gz_2010_34_140_00_500k WHERE COUNTY IN ('005','007','015')" \
	${spatial_dir}nj_2010.geojson \
	${input_dir}gz_2010_34_140_00_500k.shp
# ogrinfo ${spatial_dir}nj_2010.geojson

# filter pa counties
ogr2ogr -f GeoJSON -overwrite -sql \
	"SELECT * FROM gz_2010_42_140_00_500k WHERE COUNTY IN ('011','045','091', '101')" \
	${spatial_dir}pa_2010.geojson \
	${input_dir}gz_2010_42_140_00_500k.shp
# ogrinfo data/organized/spatial/pa_2010.geojson

# copy pa counties to a new geojson
cp ${spatial_dir}pa_2010.geojson \
	${spatial_dir}study_area_2010.geojson

# append nj counties to pa counties
ogr2ogr -f GeoJSON -overwrite -append \
	${spatial_dir}study_area_2010.geojson \
	${spatial_dir}nj_2010.geojson \
	-nln gz_2010_42_140_00_500k

# remove the individual pa and nj geojsons
rm ${spatial_dir}pa_2010.geojson ${spatial_dir}nj_2010.geojson

# reproject each phila census tract variable and convert to geojson
for year in 40 50 60
do
	input_file=${input_dir}phtr${year}.shp
	output_file=${spatial_dir}phila_${year}.geojson
	ogr2ogr -f GeoJSON -spat_srs EPSG:4326 $output_file $input_file
done