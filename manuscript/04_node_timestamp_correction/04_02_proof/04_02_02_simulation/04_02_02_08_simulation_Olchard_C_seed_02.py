#!/usr/bin/env python
# coding: utf-8

#import libraries
import time
from datetime import timedelta
from scipy.special import rel_entr
from scipy.stats import entropy
import pickle
import gc
import pandas as pd
import numpy as np
import os



#set the time and repeats for the script
shift_seconds = 10
total_shifts = 180


# File directories
input_dir = Path("../../04_01_data_wrangling/output")
output_dir = Path(".")



#Function to resample the time intervals of a dataframe
def resample_time_shifts(df, shift_seconds, total_shifts):
    df.set_index(['time'], inplace=True)
    offset_dfs = []

    for shift in range(total_shifts):
        offset = pd.Timedelta(seconds = shift_seconds * shift)

        resampled = df.resample('30min', origin='epoch', offset=offset)['id'].value_counts().reset_index()
        offset_df = resampled.pivot(index='time', columns='id', values='count').fillna(0)
        offset_df = offset_df.reindex(columns=all_tag_ids, fill_value = 0)

        offset_dfs.append(offset_df)
    
    return offset_dfs


#function to normalize each row of data
def normalize_df_rows(df):
    return df.div(df.sum(axis=1), axis=0)


#calculate KL divergence between each row of two dataframes
def calc_non_inf_kl_divs(anchor_df, shifted_test_df):
    non_inf_results = []
    # entropy_matrix = np.zeros((len(anchor_df), len(shifted_test_df)))
    for i, rowI in enumerate(anchor_df.values):
        anchor_time = anchor_df.index[i]

        for j, rowJ in enumerate(shifted_test_df.values):
            test_time = shifted_test_df.index[j]

            time_delta = anchor_time - test_time

            ent = (entropy(rowI, rowJ))
            # entropy_matrix[i, j] = ent

            if not np.isinf(ent):
                non_inf_result = {'anchor_time': anchor_time,
                                  'test_time': test_time,
                                  'time_diff': time_delta,
                                  'kl_div': ent}
                
                non_inf_results.append(non_inf_result)
    return non_inf_results


#calculate kl divergence of shifted dataframe
def calc_all_non_inf_kl_divs(anchor_df, shifted_test_dfs):
    results = []
    for shift in range(len(shifted_test_dfs)):
        print(f'Shift {shift}')
        results += calc_non_inf_kl_divs(anchor_df, shifted_test_dfs[shift])
    return pd.DataFrame(results)


# designing functions to filter each node group
def filter_olchard_c(group):
    return group.loc['2023-11-05 13:54:21' : '2023-11-24 13:15:09']


#function to filter dataframes according to kl divergence score
def process_dataframe(df, filter_value):
    # Filter rows where 'kl_div' is less than or equal to 1
    filtered_df = df[df['kl_div'] <= filter_value]
    # Sort the filtered DataFrame by 'kl_div'
    sorted_df = filtered_df.sort_values(by='kl_div', ascending=True)
    return sorted_df



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_anchors_normalized.pickle'):

    with open(f'{input_dir}/correct_node_data.pickle', 'rb') as file:
        correct_dataframes = pickle.load(file)
    with open(f'{input_dir}/station_data.pickle', 'rb') as file:
        station_dataframes = pickle.load(file)
    with open(f'{output_dir}/normalized_shifts_simulation_data_seed_02.pickle', 'rb') as file:
        normalized_shifts_simulation_data_seed_02 = pickle.load(file)
    
    ##############

    all_tag_ids = ['55331961','4B551E4B', '78780778', '4C785261', '2D661E19', '33333433', '78341E61', '52616161', '662A6107', '614B2A61', '34332A07', '612A4C1E', '2D2D612A', '2D2A7852', '07071E19', '2D192D78', '1E4B074C', '4B662A33', '19557855', '2A615252', '33663378', '5561331E', '341E4B2A', '1978782D', '2D344B2D', '19616666', '551E3307', '34783378', '66667833', '4B616652', '4C610761', '33331E55', '612A3355', '4B2D664C']

    # Correct data for anchors
    olchard_anchors_raw = {
         "Olchard_C_1": correct_dataframes['node_3750b3_beep_4_correct'],
        "Olchard_C_2": correct_dataframes['node_3750b3_beep_5_correct'],
        "Olchard_D_1": correct_dataframes['node_376a2b_beep_3_correct'],
        "Olchard_D_2": correct_dataframes['node_376a2b_beep_4_correct'],
        "Olchard_Layby": correct_dataframes['node_328f57_beep_2_correct'],
        "Olchard_SpeedCamera": correct_dataframes['node_379f1a_beep_3_correct'],
        "Olchard": station_dataframes['V30B0154C8C9']
        }
    

    #Filter anchors between specific time period
    olchard_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in olchard_anchors_raw.items()}

    #resample and normalize the anchor nodes
    olchard_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in olchard_anchors.items()}

    with open(f'{output_dir}/olchard_anchors_normalized.pickle', 'wb') as handle:
        pickle.dump(olchard_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
    with open(f'{output_dir}/olchard_anchors_normalized.pickle', 'rb') as file:
        olchard_anchors_normalized = pickle.load(file)

    with open(f'{output_dir}/normalized_shifts_simulation_data_seed_02.pickle', 'rb') as file:
        normalized_shifts_simulation_data_seed_02 = pickle.load(file)




#filter anchors per node - group 1
Olchard_C_anchors = {key: filter_olchard_c(df) for key, df in olchard_anchors_normalized.items()}



# Remove empty dataframes from the dictionary
Olchard_C_anchors = {key: df for key, df in Olchard_C_anchors.items() if not df.empty}



# Initialize the dictionary to store the samples
Olchard_C_kl_div = {}

#loop through anchors and resampled data
for size in range(100, 3100, 100):
    
    print(size)
    
    #calculate KL Divergence between each anchor
    sampled_df = {key: calc_all_non_inf_kl_divs(df, normalized_shifts_simulation_data_seed_02[f'sample_size_{size}']) for key, df in Olchard_C_anchors.items()}
    
    # Store the sampled DataFrame in the dictionary with the sample size as the key
    Olchard_C_kl_div[f'sample_size_{size}'] = sampled_df


# Using dictionary comprehensions and itertools.chain to filter out empty DataFrames in one line
Olchard_C_kl_div = {
    outer_key: {key: df for key, df in inner_dict.items() if isinstance(df, pd.DataFrame) and not df.empty}
    for outer_key, inner_dict in Olchard_C_kl_div.items()
    if any(isinstance(df, pd.DataFrame) and not df.empty for df in inner_dict.values())
}


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_kl_div.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the dictionary to store summary statistics
Olchard_C_dic_summary_stats = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Olchard_C_kl_div.items():
    # Initialize a dictionary to store the summary statistics for the current outer_key
    inner_summary_stats = {}
    
    # Iterate over the inner dictionary
    for inner_key, df in inner_dict.items():
        try:
            # Calculate summary statistics
            summary_stats = df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max'])
            inner_summary_stats[inner_key] = summary_stats
        except KeyError:
            print(f"DataFrame for key {inner_key} does not contain the required columns.")
    
    # Store the inner summary statistics in the outer dictionary
    Olchard_C_dic_summary_stats[outer_key] = inner_summary_stats


# Initialize the dictionary to store summary statistics
Olchard_C_dic_mode = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Olchard_C_kl_div.items():
    # Initialize a dictionary to store the summary statistics for the current outer_key
    inner_mode_stats = {}
    
    # Iterate over the inner dictionary
    for inner_key, df in inner_dict.items():
        try:
            # Calculate summary statistics
            mode_stats = df[['time_diff', 'kl_div']].agg(lambda x: x.mode())
            inner_mode_stats[inner_key] = mode_stats
        except KeyError:
            print(f"DataFrame for key {inner_key} does not contain the required columns.")
    
    # Store the inner summary statistics in the outer dictionary
    Olchard_C_dic_mode[outer_key] = inner_mode_stats


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_summary_stats.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_02_mode_stats.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the dictionary to store concatenated DataFrames
Olchard_C_combined_dict = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Olchard_C_kl_div.items():
    # Concatenate all DataFrames in the inner dictionary
    combined_df = pd.concat(inner_dict.values(), keys=inner_dict.keys(), names=['inner_key']).reset_index(level='inner_key').reset_index(drop=True)
    
    # Store the concatenated DataFrame in the resulting dictionary
    Olchard_C_combined_dict[outer_key] = combined_df


with open(f'{output_dir}/simulation_data_seed_02_combined_dictionary.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_combined_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
olchard_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Olchard_C_combined_dict.items()}
olchard_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Olchard_C_combined_dict.items()}


with open(f'{output_dir}/simulation_data_seed_02_combined_dictionary_summary_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_all_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_02_combined_dictionary_mode_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_all_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Olchard_C_low_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Olchard_C_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 1)
    
    # Store the processed DataFrame in the resulting dictionary
    Olchard_C_low_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_low_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_low_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
olchard_low_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Olchard_C_low_kl_div_results_table.items()}
olchard_low_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Olchard_C_low_kl_div_results_table.items()}


with open(f'{output_dir}/simulation_data_seed_02_low_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_low_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_02_low_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_low_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Olchard_C_very_low_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Olchard_C_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 0.5)
    
    # Store the processed DataFrame in the resulting dictionary
    Olchard_C_very_low_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_very_low_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_very_low_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
olchard_very_low_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Olchard_C_very_low_kl_div_results_table.items()}
olchard_very_low_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Olchard_C_very_low_kl_div_results_table.items()}


with open(f'{output_dir}/simulation_data_seed_02_very_low_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_very_low_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_02_very_low_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_very_low_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Olchard_C_zero_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Olchard_C_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 0)
    
    # Store the processed DataFrame in the resulting dictionary
    Olchard_C_zero_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_zero_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_zero_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
olchard_zero_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Olchard_C_zero_kl_div_results_table.items()}
olchard_zero_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Olchard_C_zero_kl_div_results_table.items()}


with open(f'{output_dir}/simulation_data_seed_02_zero_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_zero_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_02_zero_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(olchard_zero_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



#create variable of the true time difference
true_time_diff = pd.Timedelta('2499 days 17 hours 19 minutes 58 seconds')
true_time_diff


#calculate the error and absolute error of the estimate - all data
olchard_all_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in olchard_all_mode.items()
}


#calculate the error and absolute error of the estimate - low data
olchard_low_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in olchard_low_kl_div_mode.items()
}


#calculate the error and absolute error of the estimate - very low data
olchard_very_low_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in olchard_very_low_kl_div_mode.items()
}


#calculate the error and absolute error of the estimate - zero data
olchard_zero_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in olchard_zero_kl_div_mode.items()
}



#dictionary of the results with error estimates
Olchard_C_kl_div_error = {
    "Olchard_C_all_kl_div_error": olchard_all_mode_with_error,
    "Olchard_C_low_kl_div_error": olchard_low_kl_div_mode_with_error,
    "Olchard_C_very_low_kl_div_error": olchard_very_low_kl_div_mode_with_error,
    "Olchard_C_zero_kl_div_error": olchard_zero_kl_div_mode_with_error
}


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_02_error_estimate.pickle', 'wb') as handle:
        pickle.dump(Olchard_C_kl_div_error, handle, protocol=pickle.HIGHEST_PROTOCOL)
