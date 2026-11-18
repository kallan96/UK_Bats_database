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



#set the sample time shift and number of repeats for the script
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
def filter_huxbear(group):
    return group.loc['2023-09-19 00:00:00' : '2024-01-24 18:00:00']


#function to calculate the KL Divergerence of a selected subsample of the dataframe
def kl_div_sim_sample_size(anchors_dic, simulation_dic):
    
    # Initialize the dictionary to store the samples
    results_kl_div = {}

    # Loop through sample sizes
    for size in range(100, 3100, 100):
        print(f"Processing sample size: {size}")

        # Calculate KL Divergence between each anchor
        sampled_df = {
            key: calc_all_non_inf_kl_divs(df, simulation_dic[f'sample_size_{size}']) 
            for key, df in anchors_dic.items()
        }

        # Store the sampled DataFrame in the dictionary with the sample size as the key
        results_kl_div[f'sample_size_{size}'] = sampled_df

    return results_kl_div


#function to filter dataframes according to kl divergence score
def process_dataframe(df, filter_value):
    # Filter rows where 'kl_div' is less than or equal to 1
    filtered_df = df[df['kl_div'] <= filter_value]
    # Sort the filtered DataFrame by 'kl_div'
    sorted_df = filtered_df.sort_values(by='kl_div', ascending=True)
    return sorted_df



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/huxbear_anchors_normalized.pickle'):

    with open(f'{input_dir}/correct_node_data.pickle', 'rb') as file:
        correct_dataframes = pickle.load(file)
    with open(f'{input_dir}/station_data.pickle', 'rb') as file:
        station_dataframes = pickle.load(file)
    with open(f'{output_dir}/normalized_shifts_simulation_data_seed_04.pickle', 'rb') as file:
        normalized_shifts_simulation_data_seed_04 = pickle.load(file)
    
    ##############

    all_tag_ids = ['55331961','4B551E4B', '78780778', '4C785261', '2D661E19', '33333433', '78341E61', '52616161', '662A6107', '614B2A61', '34332A07', '612A4C1E', '2D2D612A', '2D2A7852', '07071E19', '2D192D78', '1E4B074C', '4B662A33', '19557855', '2A615252', '33663378', '5561331E', '341E4B2A', '1978782D', '2D344B2D', '19616666', '551E3307', '34783378', '66667833', '4B616652', '4C610761', '33331E55', '612A3355', '4B2D664C']

    # Correct data for anchors
    huxbear_anchors_raw = {
        "ExpressWay_1": correct_dataframes['node_376adf_beep_3_correct'],
        "ExpressWay_2": correct_dataframes['node_376adf_beep_4_correct'],
        "BatHouse_1": correct_dataframes['node_3795d0_beep_2_correct'],
        "BatHouse_2": correct_dataframes['node_3795d0_beep_3_correct'],
        "KilnWood": correct_dataframes['node_377401_beep_3_correct'],
        "Chudleigh": station_dataframes['V30B0154D392']
    }

    #Filter anchors between specific time period
    huxbear_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in huxbear_anchors_raw.items()}

    #resample and normalize the anchor nodes
    huxbear_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in huxbear_anchors.items()}

    with open(f'{output_dir}/huxbear_anchors_normalized.pickle', 'wb') as handle:
        pickle.dump(huxbear_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
    with open(f'{output_dir}/huxbear_anchors_normalized.pickle', 'rb') as file:
        huxbear_anchors_normalized = pickle.load(file)

    with open(f'{output_dir}/normalized_shifts_simulation_data_seed_04.pickle', 'rb') as file:
        normalized_shifts_simulation_data_seed_04 = pickle.load(file)



#filter anchors per node - group 1
Huxbear_anchors = {key: filter_huxbear(df) for key, df in huxbear_anchors_normalized.items()}


# Remove empty dataframes from the dictionary
Huxbear_anchors = {key: df for key, df in Huxbear_anchors.items() if not df.empty}


# Calculate KL Divergence of samples
Huxbear_kl_div = kl_div_sim_sample_size(Huxbear_anchors, normalized_shifts_simulation_data_seed_04)


# Using dictionary comprehensions and itertools.chain to filter out empty DataFrames in one line
Huxbear_kl_div = {
    outer_key: {key: df for key, df in inner_dict.items() if isinstance(df, pd.DataFrame) and not df.empty}
    for outer_key, inner_dict in Huxbear_kl_div.items()
    if any(isinstance(df, pd.DataFrame) and not df.empty for df in inner_dict.values())
}


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_04_kl_div.pickle', 'wb') as handle:
        pickle.dump(Huxbear_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the dictionary to store summary statistics
Huxbear_dic_summary_stats = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Huxbear_kl_div.items():
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
    Huxbear_dic_summary_stats[outer_key] = inner_summary_stats


# Initialize the dictionary to store summary statistics
Huxbear_dic_mode = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Huxbear_kl_div.items():
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
    Huxbear_dic_mode[outer_key] = inner_mode_stats


#write pickle file of results
with open(f'{output_dir}/simulation_data_seed_04_summary_stats.pickle', 'wb') as handle:
        pickle.dump(Huxbear_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_04_mode_stats.pickle', 'wb') as handle:
        pickle.dump(Huxbear_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the dictionary to store concatenated DataFrames
Huxbear_combined_dict = {}

# Iterate over the outer dictionary
for outer_key, inner_dict in Huxbear_kl_div.items():
    # Concatenate all DataFrames in the inner dictionary
    combined_df = pd.concat(inner_dict.values(), keys=inner_dict.keys(), names=['inner_key']).reset_index(level='inner_key').reset_index(drop=True)
    
    # Store the concatenated DataFrame in the resulting dictionary
    Huxbear_combined_dict[outer_key] = combined_df


#write pickle files of concatenated DataFrames
with open(f'{output_dir}/simulation_data_seed_04_combined_dictionary.pickle', 'wb') as handle:
        pickle.dump(Huxbear_combined_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
huxbear_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Huxbear_combined_dict.items()}
huxbear_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Huxbear_combined_dict.items()}


#write pickle files of concatenated summary statistics
with open(f'{output_dir}/simulation_data_seed_04_combined_dictionary_summary_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_all_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_04_combined_dictionary_mode_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_all_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Huxbear_low_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Huxbear_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 1)
    
    # Store the processed DataFrame in the resulting dictionary
    Huxbear_low_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of low kl divergence results
with open(f'{output_dir}/simulation_data_seed_04_low_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Huxbear_low_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
huxbear_low_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Huxbear_low_kl_div_results_table.items()}
huxbear_low_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Huxbear_low_kl_div_results_table.items()}


# write pickle file of low kl divergence summary statistics
with open(f'{output_dir}/simulation_data_seed_04_low_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_low_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_04_low_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_low_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Huxbear_very_low_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Huxbear_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 0.5)
    
    # Store the processed DataFrame in the resulting dictionary
    Huxbear_very_low_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of very low kl divergence results
with open(f'{output_dir}/simulation_data_seed_04_very_low_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Huxbear_very_low_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
huxbear_very_low_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Huxbear_very_low_kl_div_results_table.items()}
huxbear_very_low_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Huxbear_very_low_kl_div_results_table.items()}


# write pickle file of very low kl divergence summary statistics
with open(f'{output_dir}/simulation_data_seed_04_very_low_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_very_low_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_04_very_low_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_very_low_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



# Initialize the resulting dictionary
Huxbear_zero_kl_div_results_table = {}

# Iterate over the combined dictionary
for key, df in Huxbear_combined_dict.items():
    # Process the DataFrame to filter and sort it
    processed_df = process_dataframe(df, 0)
    
    # Store the processed DataFrame in the resulting dictionary
    Huxbear_zero_kl_div_results_table[key] = processed_df
    
    # Explicitly call garbage collection to free up memory
    gc.collect()


#write pickle file of zero kl divergence results
with open(f'{output_dir}/simulation_data_seed_04_zero_kl_div_results_table.pickle', 'wb') as handle:
        pickle.dump(Huxbear_zero_kl_div_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)


#Calculate summary statistics
huxbear_zero_kl_div_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Huxbear_zero_kl_div_results_table.items()}
huxbear_zero_kl_div_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Huxbear_zero_kl_div_results_table.items()}


# write pickle file of zero kl divergence summary statistics
with open(f'{output_dir}/simulation_data_seed_04_zero_kl_summary_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_zero_kl_div_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_dir}/simulation_data_seed_04_zero_kl_mode_stats.pickle', 'wb') as handle:
        pickle.dump(huxbear_zero_kl_div_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)



#create variable of the true time difference
true_time_diff = pd.Timedelta('2490 days 13 hours 9 minutes 45 seconds')
true_time_diff


#calculate the error and absolute error of the estimate - all data
huxbear_all_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in huxbear_all_mode.items()
}


#calculate the error and absolute error of the estimate - low data
huxbear_low_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in huxbear_low_kl_div_mode.items()
}


#calculate the error and absolute error of the estimate - very low data
huxbear_very_low_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in huxbear_very_low_kl_div_mode.items()
}


#calculate the error and absolute error of the estimate - zero data
huxbear_zero_kl_div_mode_with_error = {
    key: df.assign(
        error_estimate=pd.to_timedelta(df['time_diff']) - true_time_diff,
        abs_error_estimate=(pd.to_timedelta(df['time_diff']) - true_time_diff).abs()
    )
    for key, df in huxbear_zero_kl_div_mode.items()
}



#dictionary of the results with error estimates
Huxbear_kl_div_error = {
    "Huxbear_all_kl_div_error": huxbear_all_mode_with_error,
    "Huxbear_low_kl_div_error": huxbear_low_kl_div_mode_with_error,
    "Huxbear_very_low_kl_div_error": huxbear_very_low_kl_div_mode_with_error,
    "Huxbear_zero_kl_div_error": huxbear_zero_kl_div_mode_with_error
}


#write pickle file of error results
with open(f'{output_dir}/simulation_data_seed_04_error_estimate.pickle', 'wb') as handle:
        pickle.dump(Huxbear_kl_div_error, handle, protocol=pickle.HIGHEST_PROTOCOL)
