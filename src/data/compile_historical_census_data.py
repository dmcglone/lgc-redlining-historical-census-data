"""
Reformat each individual decennial dataset from social explorer
to have uniform columns and column names, regardless of whether or
not those fields are available for the year in question 
"""

import os
import pandas as pd
import numpy as np
import argparse


def census_vars_csvs(variable_names_table, yearly_table_directory):
    """Get a list of dataframes for each csv

    Args:
        variable_names_table (str): path to csv table that matches input 
                dataset variable names to project naming convention
        yearly_table_directory (str): Path to directory with input 
                yearly datasets

    Returns:
        dict: of pandas data frames in a standardized format for
                each year
    """
    variable_table = pd.read_csv(variable_names_table, na_filter=False)
    all_dfs = {}
    years = list(map(lambda x: str(x), np.arange(1940, 2020, 10)))
    for y in years:
        fname = 'variables_{}.csv'.format(y)
        raw_data = pd.read_csv(os.path.join(yearly_table_directory, fname))
        raw_data['g_yr'] = y
        key_map = variable_table[variable_table['g_yr'] == y].to_dict('list')
        key_map = {k: v[0] for k, v in key_map.items()}
        base_columns = [key_map['g_cy'], key_map['g_id'], key_map['g_st']]
        standardized = raw_data[base_columns]
        standardized.columns = ['g_cy', 'Geo_FIPS', 'g_id']
        standardized.insert(loc=0, column='g_yr', value=y)

        for key, variable in sorted(key_map.items()):
            if key not in ['I'] + list(standardized.columns):
                if not variable.startswith('Geo'):
                    variable = 'SE_' + variable
                if key_map[key] != '':
                    standardized[key] = raw_data[variable]
                else:
                    standardized[key] = None

        if y == '2010':
            acs = pd.read_csv(os.path.join(
                yearly_table_directory, 'variables_2010_acs.csv'))
            # TODO: this is also sloppy
            income_var = 'SE_' + \
                variable_table[variable_table['g_yr']
                               == '2010_acs'][['I']].values[0][0]
            standardized['I'] = acs[income_var]

        if standardized['t_h_wh'][1] != '':
            standardized['t_h_wh'] = standardized[
                't_h_wh_fm'] + standardized['t_h_wh_nf']
            standardized['t_h_or'] = standardized[
                't_h_or_fm'] + standardized['t_h_or_nf']

        all_dfs[y] = standardized

    return all_dfs


def main(variable_names_table, yearly_input_table_directory, yearly_output_table_directory):
    all_years_data_frames = census_vars_csvs(
        variable_names_table, yearly_input_table_directory)
    for key, variable in all_years_data_frames.items():
        output_file = 'census_data_{}.csv'.format(key)
        output_path = os.path.join(yearly_output_table_directory, output_file)
        variable.to_csv(output_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process historical census data')
    parser.add_argument('variable_names_table')
    parser.add_argument('yearly_input_table_directory')
    parser.add_argument('yearly_output_table_directory')
    args = parser.parse_args()
    main(args.variable_names_table, args.yearly_input_table_directory,
         args.yearly_output_table_directory)
