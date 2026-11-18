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
def filter_clay_pitts_way(group):
    return group.loc['2023-09-21 15:51:00' : '2023-11-01 10:25:00']

def filter_little_lyndridge(group):
    return group.loc['2023-09-21 17:45:00' : '2023-11-01 11:50:00']

def filter_sandygate(group):
    return group.loc['2023-09-21 17:45:00' : '2023-11-01 11:30:00']



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/sandygate_mislabelled_normalized_shifts_30min.pickle'):

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
    sandygate_anchors_raw = {
        "Stony_Copse_South": correct_dataframes['node_3750b3_beep_3_correct'],
        "Kingsteington": station_dataframes['CD74B71612A1']
    }
    
    sandygate_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in sandygate_anchors_raw.items()}

    sandygate_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in sandygate_anchors.items()}

    # Incorrect data to be adjusted
    sandygate_mislabelled_raw = {
        "Clay_Pitts_Way": incorrect_dataframes['node_327d6b_beep_0_incorrect'],
        "Little_Lyndridge_Farm": incorrect_dataframes['node_3289f3_beep_1_incorrect'],
        "Sandygate_M1": incorrect_dataframes['node_37792f_beep_2_incorrect']
    }
    
    sandygate_mislabelled = {key: df[['time', 'id']] for key, df in sandygate_mislabelled_raw.items()}
    sandygate_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in sandygate_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/sandygate_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/sandygate_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_anchors_normalized_30min.pickle', 'rb') as file:
        sandygate_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/sandygate_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        sandygate_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
claypittsway_anchors = {key: filter_clay_pitts_way(df) for key, df in sandygate_anchors_normalized.items()}
littlelyndridge_anchors = {key: filter_little_lyndridge(df) for key, df in sandygate_anchors_normalized.items()}
sandygate_m1_anchors = {key: filter_sandygate(df) for key, df in sandygate_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    claypittsway_kl_div = {key: calc_all_non_inf_kl_divs(df, sandygate_mislabelled_normalized_shifts['Clay_Pitts_Way']) for key, df in claypittsway_anchors.items()}
    littlelyndridge_kl_div = {key: calc_all_non_inf_kl_divs(df, sandygate_mislabelled_normalized_shifts['Little_Lyndridge_Farm']) for key, df in littlelyndridge_anchors.items()}
    sandygate_kl_div = {key: calc_all_non_inf_kl_divs(df, sandygate_mislabelled_normalized_shifts['Sandygate_M1']) for key, df in sandygate_m1_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    claypittsway_kl_div = {key: stats for key, stats in claypittsway_kl_div.items() if not stats.empty}
    littlelyndridge_kl_div = {key: stats for key, stats in littlelyndridge_kl_div.items() if not stats.empty}
    sandygate_kl_div = {key: stats for key, stats in sandygate_kl_div.items() if not stats.empty}
                          
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    sandygate_kl_div = {
        "Clay_Pitts_Way": claypittsway_kl_div,
        "Little_Lyndridge_Farm": sandygate2_kl_div,
        "Sandygate_M1": sandygate_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/sandygate_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_kl_div_30min.pickle', 'rb') as file:
        sandygate_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    claypittsway_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in claypittsway_kl_div.items()}
    littlelyndridge_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in littlelyndridge_kl_div.items()}
    sandygate_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in sandygate_kl_div.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    sandygate_dic_summary_stats = {
        "Clay_Pitts_Way": claypittsway_dic_summary_stats,
        "Little_Lyndridge_Farm": littlelyndridge_dic_summary_stats,
        "Sandygate_M1": sandygate_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/sandygate_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_dic_summary_stats_30min.pickle', 'rb') as file:
        sandygate_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    claypittsway_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in claypittsway_kl_div.items()}
    littlelyndridge_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in littlelyndridge_kl_div.items()}
    sandygate_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in sandygate_kl_div.items()}
    
    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    sandygate_dic_mode = {
        "Clay_Pitts_Way": claypittsway_dic_mode,
        "Little_Lyndridge_Farm": littlelyndridge_dic_mode,
        "Sandygate_M1": sandygate_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/sandygate_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_dic_mode_30min.pickle', 'rb') as file:
        sandygate_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    claypittsway_combined_df = pd.concat(claypittsway_kl_div.values(), keys = claypittsway_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    littlelyndridge_combined_df = pd.concat(littlelyndridge_kl_div.values(), keys = littlelyndridge_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    sandygate_combined_df = pd.concat(sandygate_kl_div.values(), keys = sandygate_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    sandygate_results_table = {
        "Clay_Pitts_Way": claypittsway_combined_df,
        "Little_Lyndridge_Farm": littlelyndridge_combined_df,
        "Sandygate_M1": sandygate_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/sandygate_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(sandygate_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_results_table_30min.pickle', 'rb') as file:
        sandygate_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    sandygate_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in sandygate_results_table.items()}
    sandygate_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in sandygate_results_table.items()}

    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    sandygate_grouped_summary_stats = {
        "sandygate_group_all_summary": sandygate_group_all_summary_stats,
        "sandygate_group_all_mode": sandygate_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/sandygate_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(sandygate_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_grouped_summary_stats_30min.pickle', 'rb') as file:
        sandygate_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/sandygate_correction_values.pickle') or not os.path.isfile(f'{output_dir}/sandygate_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    sandygate_correction_value = {key: df['time_diff'].iloc[-1] for key, df in sandygate_group_all_mode.items()}
    print(f"The correction values for Clay Pitts Way is {sandygate_correction_value['Clay_Pitts_Way']}.")
    print(f"The correction values for Little Lyndridge Farm is {sandygate_correction_value['Little_Lyndridge_Farm']}.")
    print(f"The correction values for Sandygate M1 is {sandygate_correction_value['Sandygate_M1']}.")
    
    #Adjust the dataframe by correction value
    claypittsway_new = incorrect_dataframes['node_327d6b_beep_0_incorrect']
    claypittsway_new['time'] = claypittsway_new['time'] + sandygate_correction_value['Clay_Pitts_Way']
    claypittsway_new
    
    littlelyndridge_new = incorrect_dataframes['node_3289f3_beep_1_incorrect']
    littlelyndridge_new['time'] = littlelyndridge_new['time'] + sandygate_correction_value['Little_Lyndridge_Farm']
    littlelyndridge_new
    
    sandygatem1_new = incorrect_dataframes['node_37792f_beep_2_incorrect']
    sandygatem1_new['time'] = sandygatem1_new['time'] + sandygate_correction_value['Sandygate_M1']
    sandygatem1_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    sandygate_corrected_data = {
        "Clay_Pitts_Way": claypittsway_new,
        "Little_Lyndridge_Farm": littlelyndridge_new,
        "Sandygate_M1": sandygatem1_new
    }

    with open(f'{output_dir}/sandygate_correction_values.pickle', 'wb') as handle:
        pickle.dump(sandygate_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/sandygate_corrected_data.pickle', 'wb') as handle:
        pickle.dump(sandygate_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/sandygate_correction_values.pickle', 'rb') as file:
        sandygate_correction_value = pickle.load(file)
    with open(f'{output_dir}/sandygate_corrected_data.pickle', 'rb') as file:
        sandygate_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
