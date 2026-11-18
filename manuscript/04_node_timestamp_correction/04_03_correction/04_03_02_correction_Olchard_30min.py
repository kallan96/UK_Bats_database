#!/usr/bin/env python
# coding: utf-8

#import libraries
import time
from datetime import timedelta
from scipy.special import rel_entr
from scipy.stats import entropy
import pickle
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
def filter_olchard_a1(group):
    return group.loc['2023-11-01 12:55:00' : '2023-11-06 10:26:35']

def filter_olchard_a2(group):
    return group.loc['2023-11-24 13:35:35' : '2023-12-02 15:46:04']

def filter_olchard_b1(group):
    return group.loc['2023-11-01 12:40:00' : '2023-11-24 13:25:12']

def filter_olchard_b2(group):
    return group.loc['2023-11-24 13:35:39' : '2024-01-22 21:54:13']

def filter_olchard_c1(group):
    return group.loc['2023-11-01 13:35:00' : '2023-11-05 13:54:21']

def filter_olchard_c2(group):
    return group.loc['2023-11-24 13:15:09' : '2023-11-25 17:23:01']

def filter_olchard_d1(group):
    return group.loc['2023-11-01 13:50:00' : '2023-11-05 14:37:06']

def filter_olchard_d2(group):
    return group.loc['2023-11-24 13:57:47' : '2023-11-25 13:42:01']



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/olchard_b_mislabelled_normalized_shifts_30min.pickle'):

    print('[[[ Loading Data ]]]')
    beforeLoadingData = time.time()
    with open(f'{input_dir}/correct_node_data.pickle', 'rb') as file:
        correct_dataframes = pickle.load(file)
    with open(f'{input_dir}/station_data.pickle', 'rb') as file:
        station_dataframes = pickle.load(file)
    with open(f'{input_dir}/incorrect_node_data.pickle', 'rb') as file:
        incorrect_dataframes = pickle.load(file)
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
    
    ##############

    print('[[[ Mangling data ]]]')
    beforeMangling = time.time()
    all_tag_ids = ['55331961','4B551E4B', '78780778', '4C785261', '2D661E19', '33333433', '78341E61', '52616161', '662A6107', '614B2A61', '34332A07', '612A4C1E', '2D2D612A', '2D2A7852', '07071E19', '2D192D78', '1E4B074C', '4B662A33', '19557855', '2A615252', '33663378', '5561331E', '341E4B2A', '1978782D', '2D344B2D', '19616666', '551E3307', '34783378', '66667833', '4B616652', '4C610761', '33331E55', '612A3355', '4B2D664C']

    # Correct data for anchors
    olchard_b_anchors_raw = {
        "Olchard_A_1": correct_dataframes['node_3750b3_beep_4_correct'],
        "Olchard_A_2": correct_dataframes['node_3750b3_beep_5_correct'],
        "Olchard_C_1": correct_dataframes['node_37792f_beep_3_correct'],
        "Olchard_C_2": correct_dataframes['node_37792f_beep_4_correct'],
        "Olchard_D_1": correct_dataframes['node_376a2b_beep_3_correct'],
        "Olchard_D_2": correct_dataframes['node_376a2b_beep_4_correct'],
        "Olchard_Layby": correct_dataframes['node_328f57_beep_2_correct'],
        "Olchard_SpeedCamera": correct_dataframes['node_379f1a_beep_3_correct'],
        "Olchard": station_dataframes['V30B0154C8C9']
    }
    
    olchard_b_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in olchard_b_anchors_raw.items()}

    olchard_b_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in olchard_b_anchors.items()}

    # Incorrect data to be adjusted
    olchard_b_mislabelled_raw = {
        "Olchard_B_1": incorrect_dataframes['node_3289f3_beep_2_incorrect'],
        "Olchard_B_2": incorrect_dataframes['node_3289f3_beep_3_incorrect']
    }
    
    olchard_b_mislabelled = {key: df[['time', 'id']] for key, df in olchard_b_mislabelled_raw.items()}
    olchard_b_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in olchard_b_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/olchard_b_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/olchard_b_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_anchors_normalized_30min.pickle', 'rb') as file:
        olchard_b_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/olchard_b_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        olchard_b_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
olchard_b1_anchors = {key: filter_olchard_b1(df) for key, df in olchard_b_anchors_normalized.items()}
olchard_b2_anchors = {key: filter_olchard_b2(df) for key, df in olchard_b_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    olchard_b1_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_b_mislabelled_normalized_shifts['Olchard_B_1']) for key, df in olchard_b1_anchors.items()}
    olchard_b2_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_b_mislabelled_normalized_shifts['Olchard_B_2']) for key, df in olchard_b2_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    olchard_b1_kl_div = {key: stats for key, stats in olchard_b1_kl_div.items() if not stats.empty}
    olchard_b2_kl_div = {key: stats for key, stats in olchard_b2_kl_div.items() if not stats.empty}
                          
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    olchard_b_kl_div = {
        "Olchard_B_1": olchard_b1_kl_div,
        "Olchard_B_2": olchard_b2_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_b_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_kl_div_30min.pickle', 'rb') as file:
        olchard_b_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    olchard_b1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_b1_kl_div.items()}
    olchard_b2_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_b2_kl_div.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    olchard_b_dic_summary_stats = {
        "Olchard_B_1": olchard_b1_dic_summary_stats,
        "Olchard_B_2": olchard_b2_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_b_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_dic_summary_stats_30min.pickle', 'rb') as file:
        olchard_b_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    olchard_b1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_b1_kl_div.items()}
    olchard_b2_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_b2_kl_div.items()}
    
    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    olchard_b_dic_mode = {
        "Olchard_B_1": olchard_b1_dic_mode,
        "Olchard_B_2": olchard_b2_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/olchard_b_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_dic_mode_30min.pickle', 'rb') as file:
        olchard_b_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    olchard_b1_combined_df = pd.concat(olchard_b1_kl_div.values(), keys = olchard_b1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_b2_combined_df = pd.concat(olchard_b2_kl_div.values(), keys = olchard_b2_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    olchard_b_results_table = {
        "Olchard_B_1": olchard_b1_combined_df,
        "Olchard_B_2": olchard_b2_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_b_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(olchard_b_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_results_table_30min.pickle', 'rb') as file:
        olchard_b_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    olchard_b_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_b_results_table.items()}
    olchard_b_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_b_results_table.items()}

    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    olchard_b_grouped_summary_stats = {
        "olchard_b_group_all_summary": olchard_b_group_all_summary_stats,
        "olchard_b_group_all_mode": olchard_b_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_b_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_b_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_grouped_summary_stats_30min.pickle', 'rb') as file:
        olchard_b_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_b_correction_values.pickle') or not os.path.isfile(f'{output_dir}/olchard_b_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    olchard_b_correction_value = {key: df['time_diff'].iloc[-1] for key, df in olchard_b_group_all_mode.items()}
    print(f"The correction values for Olchard B1 is {olchard_b_correction_value['Olchard_B_1']}.")
    print(f"The correction values for Olchard B2 is {olchard_b_correction_value['Olchard_B_2']}.")
    
    #Adjust the dataframe by correction value
    olchard_b1_new = incorrect_dataframes['node_3289f3_beep_2_incorrect']
    olchard_b1_new['time'] = olchard_b1_new['time'] + olchard_b_correction_value['Olchard_B_1']
    olchard_b1_new
    
    olchard_b2_new = incorrect_dataframes['node_3289f3_beep_3_incorrect']
    olchard_b2_new['time'] = olchard_b2_new['time'] + olchard_b_correction_value['Olchard_B_2']
    olchard_b2_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    olchard_b_corrected_data = {
        "Olchard_B_1": olchard_b1_new,
        "Olchard_B_2": olchard_b2_new
    }

    with open(f'{output_dir}/olchard_b_correction_values.pickle', 'wb') as handle:
        pickle.dump(olchard_b_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/olchard_b_corrected_data.pickle', 'wb') as handle:
        pickle.dump(olchard_b_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_b_correction_values.pickle', 'rb') as file:
        olchard_b_correction_value = pickle.load(file)
    with open(f'{output_dir}/olchard_b_corrected_data.pickle', 'rb') as file:
        olchard_b_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#Repeat for remaining nodes
#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/olchard_mislabelled_normalized_shifts_30min.pickle'):

    print('[[[ Loading Data ]]]')
    beforeLoadingData = time.time()
    with open(f'{input_dir}/correct_node_data.pickle', 'rb') as file:
        correct_dataframes = pickle.load(file)
    with open(f'{input_dir}/station_data.pickle', 'rb') as file:
        station_dataframes = pickle.load(file)
    with open(f'{input_dir}/incorrect_node_data.pickle', 'rb') as file:
        incorrect_dataframes = pickle.load(file)
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
    
    ##############

    print('[[[ Mangling data ]]]')
    beforeMangling = time.time()
    all_tag_ids = ['55331961','4B551E4B', '78780778', '4C785261', '2D661E19', '33333433', '78341E61', '52616161', '662A6107', '614B2A61', '34332A07', '612A4C1E', '2D2D612A', '2D2A7852', '07071E19', '2D192D78', '1E4B074C', '4B662A33', '19557855', '2A615252', '33663378', '5561331E', '341E4B2A', '1978782D', '2D344B2D', '19616666', '551E3307', '34783378', '66667833', '4B616652', '4C610761', '33331E55', '612A3355', '4B2D664C']

    # Correct data for anchors
    olchard_anchors_raw = {
        "Olchard_A_1": correct_dataframes['node_3750b3_beep_4_correct'],
        "Olchard_A_2": correct_dataframes['node_3750b3_beep_5_correct'],
        "Olchard_B_1": olchard_b_corrected_data['Olchard_B_1'],
        "Olchard_B_2": olchard_b_corrected_data['Olchard_B_2'],
        "Olchard_C_1": correct_dataframes['node_37792f_beep_3_correct'],
        "Olchard_C_2": correct_dataframes['node_37792f_beep_4_correct'],
        "Olchard_D_1": correct_dataframes['node_376a2b_beep_3_correct'],
        "Olchard_D_2": correct_dataframes['node_376a2b_beep_4_correct'],
        "Olchard_Layby": correct_dataframes['node_328f57_beep_2_correct'],
        "Olchard_SpeedCamera": correct_dataframes['node_379f1a_beep_3_correct'],
        "Olchard": station_dataframes['V30B0154C8C9']
    }
    
    olchard_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in olchard_anchors_raw.items()}

    olchard_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in olchard_anchors.items()}

    # Incorrect data to be adjusted
    olchard_mislabelled_raw = {
        "Olchard_A_1": incorrect_dataframes['node_3750b3_beep_4_incorrect'],
        "Olchard_A_2": incorrect_dataframes['node_3750b3_beep_5_incorrect'],
        "Olchard_C_1": incorrect_dataframes['node_37792f_beep_3_incorrect'],
        "Olchard_C_2": incorrect_dataframes['node_37792f_beep_4_incorrect'],
        "Olchard_D_1": incorrect_dataframes['node_376a2b_beep_3_incorrect'],
        "Olchard_D_2": incorrect_dataframes['node_376a2b_beep_4_incorrect']
    }
    
    olchard_mislabelled = {key: df[['time', 'id']] for key, df in olchard_mislabelled_raw.items()}
    olchard_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in olchard_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/olchard_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/olchard_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_anchors_normalized_30min.pickle', 'rb') as file:
        olchard_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/olchard_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        olchard_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
olchard_a1_anchors = {key: filter_olchard_a1(df) for key, df in olchard_anchors_normalized.items()}
olchard_a2_anchors = {key: filter_olchard_a2(df) for key, df in olchard_anchors_normalized.items()}
olchard_c1_anchors = {key: filter_olchard_c1(df) for key, df in olchard_anchors_normalized.items()}
olchard_c2_anchors = {key: filter_olchard_c2(df) for key, df in olchard_anchors_normalized.items()}
olchard_d1_anchors = {key: filter_olchard_d1(df) for key, df in olchard_anchors_normalized.items()}
olchard_d2_anchors = {key: filter_olchard_d2(df) for key, df in olchard_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    olchard_a1_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_A_1']) for key, df in olchard_a1_anchors.items()}
    olchard_a2_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_A_2']) for key, df in olchard_a2_anchors.items()}
    olchard_c1_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_C_1']) for key, df in olchard_c1_anchors.items()}
    olchard_c2_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_C_2']) for key, df in olchard_c2_anchors.items()}
    olchard_d1_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_D_1']) for key, df in olchard_d1_anchors.items()}
    olchard_d2_kl_div = {key: calc_all_non_inf_kl_divs(df, olchard_mislabelled_normalized_shifts['Olchard_D_2']) for key, df in olchard_d2_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    olchard_a1_kl_div = {key: stats for key, stats in olchard_a1_kl_div.items() if not stats.empty}
    olchard_a2_kl_div = {key: stats for key, stats in olchard_a2_kl_div.items() if not stats.empty}
    olchard_c1_kl_div = {key: stats for key, stats in olchard_c1_kl_div.items() if not stats.empty}
    olchard_c2_kl_div = {key: stats for key, stats in olchard_c2_kl_div.items() if not stats.empty}
    olchard_d1_kl_div = {key: stats for key, stats in olchard_d1_kl_div.items() if not stats.empty}
    olchard_d2_kl_div = {key: stats for key, stats in olchard_d2_kl_div.items() if not stats.empty}
                          
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    olchard_kl_div = {
        "Olchard_A_1": olchard_a1_kl_div,
        "Olchard_A_2": olchard_a2_kl_div,
        "Olchard_C_1": olchard_c1_kl_div,
        "Olchard_C_2": olchard_c2_kl_div,
        "Olchard_D_1": olchard_d1_kl_div,
        "Olchard_D_2": olchard_d2_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_kl_div_30min.pickle', 'rb') as file:
        olchard_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    olchard_a1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_a1_kl_div.items()}
    olchard_a2_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_a2_kl_div.items()}
    olchard_c1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_c1_kl_div.items()}
    olchard_c2_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_c2_kl_div.items()}
    olchard_d1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_d1_kl_div.items()}
    olchard_d2_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_d2_kl_div.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    olchard_dic_summary_stats = {
        "Olchard_A_1": olchard_a1_dic_summary_stats,
        "Olchard_A_2": olchard_a2_dic_summary_stats,
        "Olchard_C_1": olchard_c1_dic_summary_stats,
        "Olchard_C_2": olchard_c2_dic_summary_stats,
        "Olchard_D_1": olchard_d1_dic_summary_stats,
        "Olchard_D_2": olchard_d2_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_dic_summary_stats_30min.pickle', 'rb') as file:
        olchard_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    olchard_a1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_a1_kl_div.items()}
    olchard_a2_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_a2_kl_div.items()}
    olchard_c1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_c1_kl_div.items()}
    olchard_c2_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_c2_kl_div.items()}
    olchard_d1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_d1_kl_div.items()}
    olchard_d2_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_d2_kl_div.items()}
    
    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    olchard_dic_mode = {
        "Olchard_A_1": olchard_a1_dic_mode,
        "Olchard_A_2": olchard_a2_dic_mode,
        "Olchard_C_1": olchard_c1_dic_mode,
        "Olchard_C_2": olchard_c2_dic_mode,
        "Olchard_D_1": olchard_d1_dic_mode,
        "Olchard_D_2": olchard_d2_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/olchard_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_dic_mode_30min.pickle', 'rb') as file:
        olchard_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    olchard_a1_combined_df = pd.concat(olchard_a1_kl_div.values(), keys = olchard_a1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_a2_combined_df = pd.concat(olchard_a2_kl_div.values(), keys = olchard_a2_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_c1_combined_df = pd.concat(olchard_c1_kl_div.values(), keys = olchard_c1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_c2_combined_df = pd.concat(olchard_c2_kl_div.values(), keys = olchard_c2_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_d1_combined_df = pd.concat(olchard_d1_kl_div.values(), keys = olchard_d1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    olchard_d2_combined_df = pd.concat(olchard_d2_kl_div.values(), keys = olchard_d2_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    olchard_results_table = {
        "Olchard_A_1": olchard_a1_combined_df,
        "Olchard_A_2": olchard_a2_combined_df,
        "Olchard_C_1": olchard_c1_combined_df,
        "Olchard_C_2": olchard_c2_combined_df,
        "Olchard_D_1": olchard_d1_combined_df,
        "Olchard_D_2": olchard_d2_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(olchard_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_results_table_30min.pickle', 'rb') as file:
        olchard_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    olchard_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in olchard_results_table.items()}
    olchard_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in olchard_results_table.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    olchard_grouped_summary_stats = {
        "olchard_group_all_summary": olchard_group_all_summary_stats,
        "olchard_group_all_mode": olchard_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/olchard_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(olchard_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_grouped_summary_stats_30min.pickle', 'rb') as file:
        olchard_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/olchard_correction_values.pickle') or not os.path.isfile(f'{output_dir}/olchard_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    olchard_correction_value = {key: df['time_diff'].iloc[-1] for key, df in olchard_group_all_mode.items()}
    print(f"The correction values for Olchard A1 is {olchard_correction_value['Olchard_A_1']}.")
    print(f"The correction values for Olchard A2 is {olchard_correction_value['Olchard_A_2']}.")
    print(f"The correction values for Olchard C1 is {olchard_correction_value['Olchard_C_1']}.")
    print(f"The correction values for Olchard C2 is {olchard_correction_value['Olchard_C_2']}.")
    print(f"The correction values for Olchard D1 is {olchard_correction_value['Olchard_D_1']}.")
    print(f"The correction values for Olchard D2 is {olchard_correction_value['Olchard_D_2']}.")
    
    #Adjust the dataframe by correction value
    olchard_a1_new = incorrect_dataframes['node_3750b3_beep_4_incorrect']
    olchard_a1_new['time'] = olchard_a1_new['time'] + olchard_correction_value['Olchard_A_1']
    olchard_a1_new
    
    olchard_a2_new = incorrect_dataframes['node_3750b3_beep_5_incorrect']
    olchard_a2_new['time'] = olchard_a2_new['time'] + olchard_correction_value['Olchard_A_2']
    olchard_a2_new
    
    olchard_c1_new = incorrect_dataframes['node_37792f_beep_3_incorrect']
    olchard_c1_new['time'] = olchard_c1_new['time'] + olchard_correction_value['Olchard_C_1']
    olchard_c1_new
    
    olchard_c2_new = incorrect_dataframes['node_37792f_beep_4_incorrect']
    olchard_c2_new['time'] = olchard_c2_new['time'] + olchard_correction_value['Olchard_C_2']
    olchard_c2_new
    
    olchard_d1_new = incorrect_dataframes['node_376a2b_beep_3_incorrect']
    olchard_d1_new['time'] = olchard_d1_new['time'] + olchard_correction_value['Olchard_D_1']
    olchard_d1_new
    
    olchard_d2_new = incorrect_dataframes['node_376a2b_beep_4_incorrect']
    olchard_d2_new['time'] = olchard_d2_new['time'] + olchard_correction_value['Olchard_D_2']
    olchard_d2_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    olchard_corrected_data = {
        "Olchard_A_1": olchard_a1_new,
        "Olchard_A_2": olchard_a2_new,
        "Olchard_C_1": olchard_c1_new,
        "Olchard_C_2": olchard_c2_new,
        "Olchard_D_1": olchard_d1_new,
        "Olchard_D_2": olchard_d2_new
    }

    with open(f'{output_dir}/olchard_correction_values.pickle', 'wb') as handle:
        pickle.dump(olchard_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/olchard_corrected_data.pickle', 'wb') as handle:
        pickle.dump(olchard_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/olchard_correction_values.pickle', 'rb') as file:
        olchard_correction_value = pickle.load(file)
    with open(f'{output_dir}/olchard_corrected_data.pickle', 'rb') as file:
        olchard_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
