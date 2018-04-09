#!/bin/bash

# run data prep step
python src/compile_historical_census_data.py \
	data/organized/variable_names.csv \
	data/organized/ \
	data/interm/

