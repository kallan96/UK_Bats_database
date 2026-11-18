#!/usr/bin/env python
# coding: utf-8

#import libraries
import time
from datetime import timedelta
from scipy.special import rel_entr
from scipy.stats import entropy
import sqlalchemy as psql
import pickle
import pandas as pd
import numpy as np
import os


#set the time and repeats for the script
shift_seconds = 10
total_shifts = 180


# File directories
input_dir = Path("../../04_01_data_wrangling/output")
dir_path = 'path_to_folder'
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
def filter_highlandpark(group):
    return group.loc['2022-10-26 20:16:32' : '2023-05-03 17:39:38']



#Load Data from SQL
print('[[[ Loading data ]]]')
beforeLoading = time.time()
    
#connect to postgres database
engine = psql.create_engine('postgresql://user:@localhost/db_name')
bat_data = pd.read_sql_table("bat_data", engine)
test_tag_data = pd.read_sql_table("test_tag_data", engine)
    
afterLoading = time.time()
print(f'{afterLoading - beforeLoading:.2f}s')



#Edit data to correct format
print('[[[ Mangling data ]]]')
beforeMangling = time.time()
    
#edit station data into correct format
station_data = pd.concat([bat_data, test_tag_data], axis=0)
station_data = station_data.loc[(station_data['time'] >= '2023-09-01') & (station_data['time'] < '2024-01-31')]
station_data = station_data.loc[station_data['node_id'].isnull()]
station_data = station_data.drop_duplicates(subset=['tag_id', 'time', 'station_id'])
station_data['time'] = pd.to_datetime(station_data['time']).dt.tz_localize(None)
    
#match to node layout
grouped_station_data = {station_id: group[['time', 'tag_id', 'tag_rssi']] for station_id, group in station_data.groupby('station_id')}

# Rename the columns in each dataframe within the dictionary
grouped_station_data = {station_id: df.rename(columns = {'tag_id': 'id', 'tag_rssi': 'rssi'}) for station_id, df in grouped_station_data.items()}

#Load tag values
all_tag_ids = ['55331961','4B551E4B', '78780778', '1E4B1907', '4B194B55', '66522D19', '2D612A4C', '4C524B61', '2D345561', '611E4C66', '5278344B', '1E612D33', '6107191E', '66554C66', '074B6119', '34527855', '78196666', '61525507', '33196619', '07344B78', '52780707', '66661955', '342A072A', '332A1E78', '072A3419', '524B4C2D', '4B78334C', '66612D1E', '4C2A4B4B', '19334B78', '1E1E3361', '33553419', '344B3452', '664C074C', '61786652', '074C6133', '07071E33', '78334B61', '4C785261', '2D661E19', '33333433', '78341E61', '52616161', '662A6107', '614B2A61', '34332A07', '612A4C1E', '2D2D612A', '2D2A7852', '07071E19', '2D192D78', '1E4B074C', '4B662A33', '19557855', '2A615252', '33663378', '5561331E', '341E4B2A', '1978782D', '2D344B2D', '19616666', '551E3307', '34783378', '66667833', '4B616652', '4C610761', '33331E55', '612A3355', '4B2D664C']
    
# Correct data for anchors
highlandpark_anchors_raw = {
    "Cemetery_1": pd.read_csv(f'{dir_path}/379f1a/beep_0.csv', header = [0]),
    "Cemetery_2": pd.read_csv(f'{dir_path}/379f1a/beep_1.csv', header = [0]),
    "Hillfort": pd.read_csv(f'{dir_path}/376a2b/beep_0.csv', header = [0]),
    "Caves": pd.read_csv(f'{dir_path}/3288ae/beep_0.csv', header = [0]),
    "Batrun": pd.read_csv(f'{dir_path}/377401/beep_0.csv', header = [0])
}

#Filter to keep only listed tags
highlandpark_anchors = {key: df[df['id'].isin(all_tag_ids)] for key, df in highlandpark_anchors_raw.items()}

#Change time column to datetime format
highlandpark_anchors = {key: df.assign(time = pd.to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%SZ')) for key, df in highlandpark_anchors.items()}
    
highlandpark_anchors = {key: df.loc[(df['time'] >= '2022-09-25 00:00:00')][['time', 'id']] for key, df in highlandpark_anchors.items()}
highlandpark_anchors = {key: df.loc[(df['time'] <= '2023-05-11 00:00:00')][['time', 'id']] for key, df in highlandpark_anchors.items()}


# Incorrect data to be adjusted
highlandpark_mislabelled_raw = {
    "HighlandPark": pd.read_csv(f'{dir_path}/32800c - Highland Park/beep_0.csv', header = [0])
}

#Filter to keep only listed tags
highlandpark_mislabelled = {key: df[df['id'].isin(all_tag_ids)] for key, df in highlandpark_mislabelled_raw.items()}

#Change time column to datetime format
highlandpark_mislabelled = {key: df.assign(time = pd.to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%SZ')) for key, df in highlandpark_mislabelled.items()}

#Filter to keep only wrong dates
highlandpark_mislabelled = {key: df.loc[(df['time'] <= '2018-01-01 00:00:00')][['time', 'id']] for key, df in highlandpark_mislabelled.items()}

afterMangling = time.time()
print(f'{afterMangling - beforeMangling:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_anchors_normalized_30min.pickle') or not os.path.isfile(f'{output_dir}/highlandpark_mislabelled_normalized_shifts_30min.pickle'):

    print('[[[ Normalizing data ]]]')
    beforeLoading = time.time()
    
    highlandpark_anchors_normalized = {key: normalize_df_rows(resample_time_shifts(df,1,1)[0]) for key, df in highlandpark_anchors.items()}
    
    highlandpark_mislabelled_normalized_shifts = {key: list(map(normalize_df_rows, resample_time_shifts(df, shift_seconds, total_shifts))) for key, df in highlandpark_mislabelled.items()}

    afterMangling = time.time()
    print(f'{afterMangling - beforeMangling:.2f}s')

    ##############
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    with open(f'{output_dir}/highlandpark_anchors_normalized_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_anchors_normalized, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/highlandpark_mislabelled_normalized_shifts_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_mislabelled_normalized_shifts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_anchors_normalized_30min.pickle', 'rb') as file:
        highlandpark_anchors_normalized = pickle.load(file)
    with open(f'{output_dir}/highlandpark_mislabelled_normalized_shifts_30min.pickle', 'rb') as file:
        highlandpark_mislabelled_normalized_shifts = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



print('[[[ Filtering Anchors ]]]')
beforeFilteringAnchors = time.time()

#filter anchors per node - group 1
highlandpark_node_anchors = {key: filter_highlandpark(df) for key, df in highlandpark_anchors_normalized.items()}

afterFilteringAnchors = time.time()
print(f'{afterFilteringAnchors - beforeFilteringAnchors:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_kl_div_30min.pickle'):
    
    print('[[[ Entropy matrix ]]]')
    beforeEntropy = time.time()
    
    #Calculate the KL Divergence of nodes
    highlandpark_kl_div = {key: calc_all_non_inf_kl_divs(df, highlandpark_mislabelled_normalized_shifts['HighlandPark']) for key, df in highlandpark_node_anchors.items()}
    
    # Remove empty DataFrames from the dictionary
    highlandpark_kl_div = {key: stats for key, stats in highlandpark_kl_div.items() if not stats.empty}
                          
    afterEntropy = time.time()
    print(f'{afterEntropy - beforeEntropy:.2f}s')

    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of kl_divergence results
    highlandpark_node_kl_div = {
        "HighlandPark": highlandpark_kl_div
    }
    
    #write pickle file of results
    with open(f'{output_dir}/highlandpark_kl_div_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_node_kl_div, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_kl_div_30min.pickle', 'rb') as file:
        highlandpark_node_kl_div = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_dic_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - All Data ]]]')
    beforeSummaryStats = time.time()
    
    #Calculate summary statistics
    highlandpark_dic_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in highlandpark_kl_div.items()}
    
    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_summary_statsergence results
    highlandpark_node_dic_summary_stats = {
        "HighlandPark": highlandpark_dic_summary_stats
    }
    
    #write pickle file of results
    with open(f'{output_dir}/highlandpark_dic_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_node_dic_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_dic_summary_stats_30min.pickle', 'rb') as file:
        highlandpark_node_dic_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_dic_mode_30min.pickle'):
    
    print('[[[ Calculating Mode Statistics - All Data ]]]')
    beforeModeStats = time.time()
    
    #Calculate mode
    highlandpark_dic_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in highlandpark_kl_div.items()}
    
    afterModeStats = time.time()
    print(f'{afterModeStats - beforeModeStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of dic_modeergence results
    highlandpark_node_dic_mode = {
        "HighlandPark": highlandpark_dic_mode
    }

    #write pickle file of results
    with open(f'{output_dir}/highlandpark_dic_mode_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_node_dic_mode, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_dic_mode_30min.pickle', 'rb') as file:
        highlandpark_node_dic_mode = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_results_table_30min.pickle'):
    
    print('[[[ Combining Dataframes ]]]')
    beforeCombine = time.time()
    
    # Combine all DataFrames into a single DataFrame
    highlandpark_combined_df = pd.concat(highlandpark_kl_div.values(), keys = highlandpark_kl_div.keys(), names = ['anchor_node']).reset_index(level = 'anchor_node').reset_index(drop = True)
    
    afterCombine = time.time()
    print(f'{afterCombine - beforeCombine:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    highlandpark_node_results_table = {
        "HighlandPark": highlandpark_combined_df
    }
    
    #write pickle file of results
    with open(f'{output_dir}/highlandpark_results_table_30min.pickle', 'wb') as handle:
            pickle.dump(highlandpark_node_results_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_results_table_30min.pickle', 'rb') as file:
        highlandpark_node_results_table = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_grouped_summary_stats_30min.pickle'):
    
    print('[[[ Calculating Summary Statistics - Grouped Data ]]]')
    beforeSummaryStats = time.time()

    #Calculate summary statistics
    highlandpark_group_all_summary_stats = {key: df[['time_diff', 'kl_div']].agg(['count', 'mean', 'median', 'std', 'min', 'max']) for key, df in highlandpark_node_results_table.items()}
    highlandpark_group_all_mode = {key: df[['time_diff', 'kl_div']].agg(lambda x: x.mode()) for key, df in highlandpark_node_results_table.items()}

    afterSummaryStats = time.time()
    print(f'{afterSummaryStats - beforeSummaryStats:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()

    # create dictionary of result tables
    highlandpark_grouped_summary_stats = {
        "highlandpark_group_all_summary": highlandpark_group_all_summary_stats,
        "highlandpark_group_all_mode": highlandpark_group_all_mode
    }
    
    #write pickle file of results
    with open(f'{output_dir}/highlandpark_grouped_summary_stats_30min.pickle', 'wb') as handle:
        pickle.dump(highlandpark_grouped_summary_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_grouped_summary_stats_30min.pickle', 'rb') as file:
        highlandpark_grouped_summary_stats = pickle.load(file)
    
    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')



#check for pickle files, if they aren't in the directory create them
if not os.path.isfile(f'{output_dir}/highlandpark_correction_values.pickle') or not os.path.isfile(f'{output_dir}/highlandpark_corrected_data.pickle'):

    print('[[[ Adjusting data by correction value ]]]')
    beforeCalculating = time.time()
    
    #Extract the correction value for each node
    highlandpark_correction_value = {key: df['time_diff'].iloc[-1] for key, df in highlandpark_group_all_mode.items()}
    print(f"The correction values for Highland Park is {highlandpark_correction_value['HighlandPark']}.")
    
    #Adjust the dataframe by correction value
    highlandpark_new = pd.read_csv(f'{dir_path}/32800c - Highland Park/beep_0.csv', header = [0])
    highlandpark_new['time'] = pd.to_datetime(highlandpark_new['time'], format='%Y-%m-%dT%H:%M:%SZ')
    highlandpark_new = highlandpark_new.loc[(highlandpark_new['time'] <= '2018-01-01 00:00:00')]
    highlandpark_new['time'] = highlandpark_new['time'] + highlandpark_correction_value['HighlandPark']
    highlandpark_new
    
    afterCalculating = time.time()
    print(f'{afterCalculating - beforeCalculating:.2f}s')
    
    print('[[[ Writing data ]]]')
    beforeWriting = time.time()
    
    # create dictionary of result tables
    highlandpark_corrected_data = {
        "HighlandPark": highlandpark_new
    }

    with open(f'{output_dir}/highlandpark_correction_values.pickle', 'wb') as handle:
        pickle.dump(highlandpark_correction_value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_dir}/highlandpark_corrected_data.pickle', 'wb') as handle:
        pickle.dump(highlandpark_corrected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    AfterWriting = time.time()
    print(f'{AfterWriting - beforeWriting:.2f}s')

else:
    print('[[[ Loading data ]]]')
    beforeLoadingData = time.time()

    with open(f'{output_dir}/highlandpark_correction_values.pickle', 'rb') as file:
        highlandpark_correction_value = pickle.load(file)
    with open(f'{output_dir}/highlandpark_corrected_data.pickle', 'rb') as file:
        highlandpark_corrected_data = pickle.load(file)

    afterLoadingData = time.time()
    print(f'{afterLoadingData - beforeLoadingData:.2f}s')
