# Historical Demograhic Data

This repository contains raw datasets and scripts used to create a set of historical spatial datasets of demographic variables in the Greater Philadelphia area.


### Getting started

This project uses the Azavea Data Analytics team's [Python Project Template](https://github.com/azavea/python-project-template). Before commencing with data analysis, follow the instructions in the `Getting Started` section of the project templates's [documentation](https://github.com/azavea/python-project-template/blob/master/README.md).

The first step is to download the necessary census variables for each year from [Social Explorer](https://www.socialexplorer.com/). 

* Select `Tables` from the top menu bar
* For each decennial census year 1940 - 2010, download the necessary table
    - For years 1940, 1950 and 1960, use the `U.S. Decennial Census` dropdown options. For all other years, use the `U.S. Decennial Census on 2010 Geographies` 
    - Click `Begin Report` for the year in question
    - Select census tracts by county and include the following counties in PA and NJ: `Philadelphia County, PA`, `Berks County, PA`, `Montgomery County, PA`, `Delaware County, PA`, `Camden County, NJ`, `Burlington County, NJ`, and `Gloucester County, NJ`
    - Locate the data dictionary for the year you are searching for. These text files are located in `data/doc/data-dictionaries/`. 
    - Select each of the tables listed in this file and download the data as a csv. Place it in `data/raw`
    - Copy the csv to `data/organized` and change it's name based on it's year so that it matches the following convention: `variables_YYYY.csv`
* You will also need the `variable_names.csv` dataset located in `/data`

You are now set up to run the script that generates decennial census tables in a standardized format. From within the home directory of the Docker container run

`python src/data/compile_historical_census_data.py data/organized/variable_names.csv data/organized/ data/interim/`

Note: Not all variables and/or geographies are available for each year

Next, generate a set of lookup tables that associate historical census tracts with contemporary tracts and tracts with neighborhoods. From root project directory run:

`python src/data/generate_tract_lookups.py data/organized/spatial/study_area_2010.geojson data/organized/spatial/ data/organized/spatial/Neighborhoods_Philadelphia.geojson data/interim/historical_tract_lookup.csv`

### Understanding the output

This project will output a series of shapefiles. All shapefiles will have the same fields. However, for most shapefiles, many fields will be populated with NA values indicating that a variable is not available for that year.

### Variable naming convention

Because of the sophisticated nature of some of these variables and the character limits on shapefile field names, I have created a naming convention for the census fields in this shapefile. 

Variable descriptions are represented by a series of 1-2 character variables separated by `_`. The values associated with each key are as follows:

| key | value |
|-------|---------:|
||
|*variable type*||
|t|total|
|c|percent|
|g|identifier|
||
|*identifier*||
|id|fips code|
|st|state|
|cy|county|
|y|year|
||
|*universe*||
|p|population|
|h|household|
|I|median household income|
|u|housing units|
||
|*operator*||
|n|not|
||
|*race*||
|wh|white|
|bl|black|
|as|asian|
|na|native american|
|nh|native hawaiian/pacific islander|
|or|other race|
|mr|mixed race|
||
|*ethnicity*||
|wa,white alone|not hispanic or latino|
|hi|hispanic|
|nw|not White Alone, or is Hispanic or Latino|
||
|*household family status*||
|nf|non family|
|fm|family|
||
|*housing unit occupancy status*||
|oc|occupied|
|vc|vacant|
||
|*housing unit tenure*||
|ro|renter occupied|
|oo|owner occupied|

For each variable name, the first key will indicate the variable type: is it a raw total, a percent or an identifier. The second will indicate the 'universe' (i.e. what is being counted). The rest will modify the variable. 

For example:
`g_st` = Home state
`t_p` = Total population
`t_h_wh` = Total households with a white head of household
`t_u_oc_oo` = Total occupied housing units that are owner occupied

Note: all percentages are represented as decimals  
