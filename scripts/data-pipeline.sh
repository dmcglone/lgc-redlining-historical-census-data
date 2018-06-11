#!/bin/bash

python3 src/data/compile_historical_census_data.py \
	data/organized/variable_names.csv \
	data/organized/ \
	data/interim/

python3 src/data/generate_tract_lookups.py \
	data/organized/spatial/study_area_2010.geojson \
	data/organized/spatial/ \
	data/organized/spatial/Neighborhoods_Philadelphia.geojson \
	data/interim/historical_tract_lookup.csv
