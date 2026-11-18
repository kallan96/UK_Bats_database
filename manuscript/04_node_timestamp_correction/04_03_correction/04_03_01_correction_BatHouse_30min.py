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
def filter_expressway_1(group):
    return group.loc['2023-09-22 09:19:00' : '2023-09-23 17:17:47']

def filter_kilnwood(group):
    return group.loc['2023-09-21 17:59:00' : '2023-09-26 18:50:30']

def filter_businesspark_1(group):
    return group.loc['2023-09-21 12:03:00' : '2023-10-31 16:03:34']

def filter_teignbridge_1(group):
    return group.loc['2023-09-23 10:11:00' : '2023-10-31 13:26:22']

def filter_lawelldownwood_1(group):
    return group.loc['2023-09-20 13:18:00' : '2023-11-23 20:02:40']

def filter_winstowcottages_1(group):
    return group.loc['2023-09-20 14:20:00' : '2023-10-30 20:45:17']

def filter_underpass_1(group):
    return group.loc['2023-09-21 11:12:00' : '2023-10-30 21:05:47']

def filter_lawellhouse_1(group):
    return group.loc['2023-09-20 12:49:00' : '2023-11-24 15:00:02']

def filter_cowcave_1(group):
    return group.loc['2023-09-20 11:25:14' : '2023-11-24 15:10:02']

def filter_gappahcows_1(group):
    return group.loc['2023-09-21 12:35:00' : '2023-10-31 16:57:16']



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_gappah_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/bathouse_gappah_mislabelled_normalized_shifts_30min.pickle'):

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
    bathouse_anchors_raw = {
        "Gappah": station_dataframes['V30B0154EBA8'],
        "Palace_Meadow": station_dataframes['31D096AEC921']
    }
    bathouse_anchors = {key: df.loc[(df['time'] >= '2023-09-18 23:00:00')][['time', 'id']] for key, df in bathouse_anchors_raw.items()}
    
    bathouse_anchors = {key: df.loc[(df['time'] <= '2023-11-25 23:00:00')][['time', 'id']] for key, df in bathouse_anchors.items()}

    bathouse_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in bathouse_anchors.items()}

    # Incorrect data to be adjusted
    bathouse_mislabelled_raw = {
        "ExpressWay_1": incorrect_dataframes['node_376adf_beep_3_incorrect'],
        "KilnWood": incorrect_dataframes['node_377401_beep_3_incorrect'],
        "BusinessPark_1": incorrect_dataframes['node_32800c_beep_1_incorrect'],
        "TeignBridge_1": incorrect_dataframes['node_37920b_beep_1_incorrect'],
        "LawelldownWood_1": incorrect_dataframes['node_37807e_beep_1_incorrect'],
        "WinstowCottages_1": incorrect_dataframes['node_3781a5_beep_1_incorrect'],
        "Underpass_1": incorrect_dataframes['node_376f37_beep_2_incorrect'],
        "LawellHouse_1": incorrect_dataframes['node_328787_beep_3_incorrect'],
        "CowCave_1": incorrect_dataframes['node_3292c8_beep_3_incorrect'],
        "GappahCows_1": incorrect_dataframes['node_32b6e0_beep_5_incorrect']
    }
    bathouse_mislabelled = {key: df[['time', 'id']] for key, df in bathouse_mislabelled_raw.items()}
    bathouse_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in bathouse_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/bathouse_gappah_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/bathouse_gappah_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_gappah_anchors_normalized_30min.pickle', 'rb') as file:
        bathouse_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/bathouse_gappah_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        bathouse_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
ExpressWay_1_anchors = {key: filter_expressway_1(df) for key, df in bathouse_anchors_normalized.items()}
KilnWood_anchors = {key: filter_kilnwood(df) for key, df in bathouse_anchors_normalized.items()}
BusinessPark_1_anchors = {key: filter_businesspark_1(df) for key, df in bathouse_anchors_normalized.items()}
TeignBridge_1_anchors = {key: filter_teignbridge_1(df) for key, df in bathouse_anchors_normalized.items()}
LawelldownWood_1_anchors = {key: filter_lawelldownwood_1(df) for key, df in bathouse_anchors_normalized.items()}
WinstowCottages_1_anchors = {key: filter_winstowcottages_1(df) for key, df in bathouse_anchors_normalized.items()}
Underpass_1_anchors = {key: filter_underpass_1(df) for key, df in bathouse_anchors_normalized.items()}
LawellHouse_1_anchors = {key: filter_lawellhouse_1(df) for key, df in bathouse_anchors_normalized.items()}
CowCave_1_anchors = {key: filter_cowcave_1(df) for key, df in bathouse_anchors_normalized.items()}
GappahCows_1_anchors = {key: filter_gappahcows_1(df) for key, df in bathouse_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_gappah_all_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    ExpressWay_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['ExpressWay_1']) for key, df in ExpressWay_1_anchors.items()}
    KilnWood_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['KilnWood']) for key, df in KilnWood_anchors.items()}
    BusinessPark_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['BusinessPark_1']) for key, df in BusinessPark_1_anchors.items()}
    TeignBridge_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['TeignBridge_1']) for key, df in TeignBridge_1_anchors.items()}
    LawelldownWood_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['LawelldownWood_1']) for key, df in LawelldownWood_1_anchors.items()}
    WinstowCottages_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['WinstowCottages_1']) for key, df in WinstowCottages_1_anchors.items()}
    Underpass_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['Underpass_1']) for key, df in Underpass_1_anchors.items()}
    LawellHouse_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['LawellHouse_1']) for key, df in LawellHouse_1_anchors.items()}
    CowCave_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['CowCave_1']) for key, df in CowCave_1_anchors.items()}
    GappahCows_1_kl_div = {key: calc_all_non_inf_kl_divs(df, bathouse_mislabelled_normalized_shifts['GappahCows_1']) for key, df in GappahCows_1_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    ExpressWay_1_kl_div = {key: stats for key, stats in ExpressWay_1_kl_div.items() if not stats.empty}
    KilnWood_kl_div = {key: stats for key, stats in KilnWood_kl_div.items() if not stats.empty}
    BusinessPark_1_kl_div = {key: stats for key, stats in BusinessPark_1_kl_div.items() if not stats.empty}
    TeignBridge_1_kl_div = {key: stats for key, stats in TeignBridge_1_kl_div.items() if not stats.empty}
    LawelldownWood_1_kl_div = {key: stats for key, stats in LawelldownWood_1_kl_div.items() if not stats.empty}
    WinstowCottages_1_kl_div = {key: stats for key, stats in WinstowCottages_1_kl_div.items() if not stats.empty}
    Underpass_1_kl_div = {key: stats for key, stats in Underpass_1_kl_div.items() if not stats.empty}
    LawellHouse_1_kl_div = {key: stats for key, stats in LawellHouse_1_kl_div.items() if not stats.empty}
    CowCave_1_kl_div = {key: stats for key, stats in CowCave_1_kl_div.items() if not stats.empty}
    GappahCows_1_kl_div = {key: stats for key, stats in GappahCows_1_kl_div.items() if not stats.empty}
                           
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    bathouse_all_kl_div = {
        "ExpressWay_1": ExpressWay_1_kl_div,
        "KilnWood": KilnWood_kl_div,
        "BusinessPark_1": BusinessPark_1_kl_div,
        "TeignBridge_1": TeignBridge_1_kl_div,
        "LawelldownWood_1": LawelldownWood_1_kl_div,
        "WinstowCottages_1": WinstowCottages_1_kl_div,
        "Underpass_1": Underpass_1_kl_div,
        "LawellHouse_1": LawellHouse_1_kl_div,
        "CowCave_1": CowCave_1_kl_div,
        "GappahCows_1": GappahCows_1_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/bathouse_gappah_all_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_all_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_gappah_all_kl_div_30min.pickle', 'rb') as file:
        bathouse_all_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_all_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    BusinessPark_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in BusinessPark_1_kl_div.items()}
    TeignBridge_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in TeignBridge_1_kl_div.items()}
    LawelldownWood_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in LawelldownWood_1_kl_div.items()}
    WinstowCottages_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in WinstowCottages_1_kl_div.items()}
    Underpass_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in Underpass_1_kl_div.items()}
    LawellHouse_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in LawellHouse_1_kl_div.items()}
    CowCave_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in CowCave_1_kl_div.items()}
    GappahCows_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in GappahCows_1_kl_div.items()}
        
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    bathouse_all_dic_summary_stats = {
        "BusinessPark_1": BusinessPark_1_dic_summary_stats,
        "TeignBridge_1": TeignBridge_1_dic_summary_stats,
        "LawelldownWood_1": LawelldownWood_1_dic_summary_stats,
        "WinstowCottages_1": WinstowCottages_1_dic_summary_stats,
        "Underpass_1": Underpass_1_dic_summary_stats,
        "LawellHouse_1": LawellHouse_1_dic_summary_stats,
        "CowCave_1": CowCave_1_dic_summary_stats,
        "GappahCows_1": GappahCows_1_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/bathouse_all_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_all_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_all_dic_summary_stats_30min.pickle', 'rb') as file:
        bathouse_all_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_all_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    BusinessPark_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in BusinessPark_1_kl_div.items()}
    TeignBridge_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in TeignBridge_1_kl_div.items()}
    LawelldownWood_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in LawelldownWood_1_kl_div.items()}
    WinstowCottages_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in WinstowCottages_1_kl_div.items()}
    Underpass_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in Underpass_1_kl_div.items()}
    LawellHouse_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in LawellHouse_1_kl_div.items()}
    CowCave_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in CowCave_1_kl_div.items()}
    GappahCows_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in GappahCows_1_kl_div.items()}

    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    bathouse_all_dic_mode = {
        "BusinessPark_1": BusinessPark_1_dic_mode,
        "TeignBridge_1": TeignBridge_1_dic_mode,
        "LawelldownWood_1": LawelldownWood_1_dic_mode,
        "WinstowCottages_1": WinstowCottages_1_dic_mode,
        "Underpass_1": Underpass_1_dic_mode,
        "LawellHouse_1": LawellHouse_1_dic_mode,
        "CowCave_1": CowCave_1_dic_mode,
        "GappahCows_1": GappahCows_1_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/bathouse_all_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_all_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_all_dic_mode_30min.pickle', 'rb') as file:
        bathouse_all_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_all_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    BusinessPark_1_combined_df = pd.concat(BusinessPark_1_kl_div.values(), keys = BusinessPark_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    TeignBridge_1_combined_df = pd.concat(TeignBridge_1_kl_div.values(), keys = TeignBridge_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    LawelldownWood_1_combined_df = pd.concat(LawelldownWood_1_kl_div.values(), keys = LawelldownWood_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    WinstowCottages_1_combined_df = pd.concat(WinstowCottages_1_kl_div.values(), keys = WinstowCottages_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    Underpass_1_combined_df = pd.concat(Underpass_1_kl_div.values(), keys = Underpass_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    LawellHouse_1_combined_df = pd.concat(LawellHouse_1_kl_div.values(), keys = LawellHouse_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    CowCave_1_combined_df = pd.concat(CowCave_1_kl_div.values(), keys = CowCave_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    GappahCows_1_combined_df = pd.concat(GappahCows_1_kl_div.values(), keys = GappahCows_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    bathouse_all_results_table = {
        "BusinessPark_1": BusinessPark_1_combined_df,
        "TeignBridge_1": TeignBridge_1_combined_df,
        "LawelldownWood_1": LawelldownWood_1_combined_df,
        "WinstowCottages_1": WinstowCottages_1_combined_df,
        "Underpass_1": Underpass_1_combined_df,
        "LawellHouse_1": LawellHouse_1_combined_df,
        "CowCave_1": CowCave_1_combined_df,
        "GappahCows_1": GappahCows_1_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/bathouse_all_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(bathouse_all_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_all_results_table_30min.pickle', 'rb') as file:
        bathouse_all_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    bathouse_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in bathouse_all_results_table.items()}
    bathouse_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in bathouse_all_results_table.items()}

    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    bathouse_grouped_summary_stats = {
        "bathouse_group_all_summary": bathouse_group_all_summary_stats,
        "bathouse_group_all_mode": bathouse_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/bathouse_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(bathouse_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_grouped_summary_stats_30min.pickle', 'rb') as file:
        bathouse_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/bathouse_correction_values.pickle') or not os.path.isfile(f'{output_dir}/bathouse_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    bathouse_correction_value = {key: df['time_diff'].iloc[-1] for key, df in bathouse_group_all_mode.items()}
    print(f"The correction values for Clifford Business Park 1 is {bathouse_correction_value['BusinessPark_1']}.")
    print(f"The correction values for Teign Bridge 1 is {bathouse_correction_value['TeignBridge_1']}.")
    print(f"The correction values for Lawelldown Wood 1 is {bathouse_correction_value['LawelldownWood_1']}.")
    print(f"The correction values for Winstow Cottages 1 is {bathouse_correction_value['WinstowCottages_1']}.")
    print(f"The correction values for Kate Brook Underpass 1 is {bathouse_correction_value['Underpass_1']}.")
    print(f"The correction values for Lawell House 1 is {bathouse_correction_value['LawellHouse_1']}.")
    print(f"The correction values for Cow Cave Wood 1 is {bathouse_correction_value['CowCave_1']}.")
    print(f"The correction values for Gappah Cows 1 is {bathouse_correction_value['GappahCows_1']}.")
    
    #Adjust the dataframe by correction value
    businesspark1_new = incorrect_dataframes['node_32800c_beep_1_incorrect']
    businesspark1_new['time'] = businesspark1_new['time'] + bathouse_correction_value['BusinessPark_1']
    businesspark1_new

    teignbridge1_new = incorrect_dataframes['node_37920b_beep_1_incorrect']
    teignbridge1_new['time'] = teignbridge1_new['time'] + bathouse_correction_value['TeignBridge_1']
    teignbridge1_new
    
    lawelldownwood1_new = incorrect_dataframes['node_37807e_beep_1_incorrect']
    lawelldownwood1_new['time'] = lawelldownwood1_new['time'] + bathouse_correction_value['LawelldownWood_1']
    lawelldownwood1_new
    
    winstowcottages1_new = incorrect_dataframes['node_3781a5_beep_1_incorrect']
    winstowcottages1_new['time'] = winstowcottages1_new['time'] + bathouse_correction_value['WinstowCottages_1']
    winstowcottages1_new

    underpass1_new = incorrect_dataframes['node_376f37_beep_2_incorrect']
    underpass1_new['time'] = underpass1_new['time'] + bathouse_correction_value['Underpass_1']
    underpass1_new
    
    lawellhouse1_new = incorrect_dataframes['node_328787_beep_3_incorrect']
    lawellhouse1_new['time'] = lawellhouse1_new['time'] + bathouse_correction_value['LawellHouse_1']
    lawellhouse1_new
    
    cowcave1_new = incorrect_dataframes['node_3292c8_beep_3_incorrect']
    cowcave1_new['time'] = cowcave1_new['time'] + bathouse_correction_value['CowCave_1']
    cowcave1_new

    gappahcows1_new = incorrect_dataframes['node_32b6e0_beep_5_incorrect']
    gappahcows1_new['time'] = gappahcows1_new['time'] + bathouse_correction_value['GappahCows_1']
    gappahcows1_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    bathouse_corrected_data = {
        "BusinessPark_1": businesspark1_new,
        "TeignBridge_1": teignbridge1_new,
        "LawelldownWood_1": lawelldownwood1_new,
        "WinstowCottages_1": winstowcottages1_new,
        "Underpass_1": underpass1_new,
        "LawellHouse_1": lawellhouse1_new,
        "CowCave_1": cowcave1_new,
        "GappahCows_1": gappahcows1_new
    }

    with open(f'{output_dir}/bathouse_correction_values.pickle', 'wb') as handle:
        pickle.dump(bathouse_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/bathouse_corrected_data.pickle', 'wb') as handle:
        pickle.dump(bathouse_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/bathouse_correction_values.pickle', 'rb') as file:
        bathouse_correction_value = pickle.load(file)
    with open(f'{output_dir}/bathouse__corrected_data.pickle', 'rb') as file:
        bathouse_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#Repeat for remaining nodes
#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/kilnwood_mislabelled_normalized_shifts_30min.pickle'):

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
    kilnwood_anchors_raw = {
        "ExpressWay_1": correct_dataframes['node_376adf_beep_3_correct'],
        "ExpressWay_2": correct_dataframes['node_376adf_beep_4_correct'],
        "BatHouse_1": correct_dataframes['node_3795d0_beep_2_correct'],
        "BatHouse_2": correct_dataframes['node_3795d0_beep_3_correct'],
        "KilnWood": correct_dataframes['node_377401_beep_3_correct'],
        "Huxbear_Vineyard": station_dataframes['CFF730D7207F'],
        "Chudleigh": station_dataframes['V30B0154D392'],
        "LawelldownWood_1": bathouse_corrected_data['LawelldownWood_1'],
        "WinstowCottages_1": bathouse_corrected_data['WinstowCottages_1'],
        "WinstowCottages_2": bathouse_corrected_data['WinstowCottages_2'],
        "WinstowCottages_3": bathouse_corrected_data['WinstowCottages_3'],
        "Underpass_3": bathouse_corrected_data['Underpass_3'],
        "LawellHouse_1": bathouse_corrected_data['LawellHouse_1'],
        "LawellHouse_2": bathouse_corrected_data['LawellHouse_2'],
        "CowCave_1": bathouse_corrected_data['CowCave_1'],
        "CowCave_2": bathouse_corrected_data['CowCave_2'],
        "GappahCows_1": bathouse_corrected_data['GappahCows_1'],
        "GappahCows_2": bathouse_corrected_data['GappahCows_2'],
        "GappahCows_3": bathouse_corrected_data['GappahCows_3']
    }
    
    kilnwood_anchors = {key: df.loc[(df['time'] >= '2023-09-19 00:00:00')][['time', 'id']] for key, df in kilnwood_anchors_raw.items()}

    kilnwood_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in kilnwood_anchors.items()}

    # Incorrect data to be adjusted
    kilnwood_mislabelled_raw = {
        "ExpressWay_1": incorrect_dataframes['node_376adf_beep_3_incorrect'],
        "KilnWood": incorrect_dataframes['node_377401_beep_3_incorrect'],
    }
    
    kilnwood_mislabelled = {key: df[['time', 'id']] for key, df in kilnwood_mislabelled_raw.items()}
    kilnwood_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in kilnwood_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/kilnwood_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/kilnwood_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_anchors_normalized_30min.pickle', 'rb') as file:
        kilnwood_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/kilnwood_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        kilnwood_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
ExpressWay_1_anchors = {key: filter_expressway_1(df) for key, df in kilnwood_anchors_normalized.items()}
KilnWood_anchors = {key: filter_kilnwood(df) for key, df in kilnwood_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_all_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    ExpressWay_1_kl_div = {key: calc_all_non_inf_kl_divs(df, kilnwood_mislabelled_normalized_shifts['ExpressWay_1']) for key, df in ExpressWay_2_anchors.items()}
    KilnWood_kl_div = {key: calc_all_non_inf_kl_divs(df, kilnwood_mislabelled_normalized_shifts['KilnWood']) for key, df in BusinessPark_3_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    ExpressWay_1_kl_div = {key: stats for key, stats in ExpressWay_1_kl_div.items() if not stats.empty}
    KilnWood_kl_div = {key: stats for key, stats in KilnWood_kl_div.items() if not stats.empty}
                           
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    kilnwood_all_kl_div = {
        "ExpressWay_2": ExpressWay_1_kl_div,
        "KilnWood": KilnWood_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/kilnwood_all_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_all_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_all_kl_div_30min.pickle', 'rb') as file:
        kilnwood_all_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_all_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    ExpressWay_1_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in ExpressWay_1_kl_div.items()}
    KilnWood_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in KilnWood_kl_div.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    kilnwood_all_dic_summary_stats = {
        "ExpressWay_1": ExpressWay_1_dic_summary_stats,
        "KilnWood": KilnWood_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/kilnwood_all_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_all_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_all_dic_summary_stats_30min.pickle', 'rb') as file:
        kilnwood_all_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_all_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    ExpressWay_1_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in ExpressWay_1_kl_div.items()}
    KilnWood_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in KilnWood_kl_div.items()}
    
    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    kilnwood_all_dic_mode = {
        "ExpressWay_1": ExpressWay_1_dic_mode,
        "KilnWood_1": KilnWood_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/kilnwoo_rerund_all_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_all_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_all_dic_mode_30min.pickle', 'rb') as file:
        kilnwood_all_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_all_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    ExpressWay_1_combined_df = pd.concat(ExpressWay_1_kl_div.values(), keys = ExpressWay_1_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    KilnWood_combined_df = pd.concat(KilnWood_kl_div.values(), keys = KilnWood_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
        
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    kilnwood_all_results_table = {
        "ExpressWay_1": ExpressWay_1_combined_df,
        "KilnWood": KilnWood_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/kilnwood_all_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(kilnwood_all_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_all_results_table_30min.pickle', 'rb') as file:
        kilnwood_all_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    kilnwood_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in kilnwood_all_results_table.items()}
    kilnwood_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in kilnwood_all_results_table.items()}

    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    kilnwood_grouped_summary_stats = {
        "kilnwood_group_all_summary": kilnwood_group_all_summary_stats,
        "kilnwood_group_all_mode": kilnwood_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/kilnwood_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(kilnwood_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_grouped_summary_stats_30min.pickle', 'rb') as file:
        kilnwood_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/kilnwood_correction_values.pickle') or not os.path.isfile(f'{output_dir}/kilnwood_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    kilnwood_correction_value = {key: df['time_diff'].iloc[-1] for key, df in kilnwood_group_all_mode.items()}
    print(f"The correction values for Express Way Lay-By 1 is {kilnwood_correction_value['ExpressWay_1']}.")
    print(f"The correction values for Kiln Wood is {kilnwood_correction_value['KilnWood']}.")
    
    #Adjust the dataframe by correction value
    expressway1_new = incorrect_dataframes['node_376adf_beep_3_incorrect']
    expressway1_new['time'] = expressway1_new['time'] + kilnwood_correction_value['ExpressWay_1']
    expressway1_new
    
    kilnwood_new = incorrect_dataframes['node_377401_beep_3_incorrect']
    kilnwood_new['time'] = kilnwood_new['time'] + kilnwood_correction_value['KilnWood']
    kilnwood_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    kilnwood_corrected_data = {
        "ExpressWay_1": expressway1_new,
        "KilnWood": kilnwood_new
    }

    with open(f'{output_dir}/kilnwood_correction_values.pickle', 'wb') as handle:
        pickle.dump(kilnwood_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/kilnwood_corrected_data.pickle', 'wb') as handle:
        pickle.dump(kilnwood_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/kilnwood_correction_values.pickle', 'rb') as file:
        kilnwood_correction_value = pickle.load(file)
    with open(f'{output_dir}/kilnwood_corrected_data.pickle', 'rb') as file:
        kilnwood_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
