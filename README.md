# UK_Bats Database

This repository contains the code used to create and populate the database supporting my PhD research at the University of Sussex. The database brings together data collected from an Automated Radio Telemetry System (ARTS; produced by Cellular Tracking Technologies (CTT)), providing a central resource for subsequent analyses.

The database was developed to support research into the ecology, movement and activity of bats, with a particular focus on greater horseshoe bats (*Rhinolophus ferrumequinum*).

## Repository contents

This repository contains the code and supporting files used to construct the database, including:

- Scripts for creating the database and its tables.
- Code for importing and processing data from different sources.
- Queries and scripts used to organise and extract data for analysis.
- Supporting documentation describing the database structure and workflow.

## Database

The database was implemented using PostgreSQL.

The code in this repository documents the database construction process, including the organisation of data and the steps required to prepare datasets for subsequent analyses.

Please note that the repository contains the code used to construct the database; it may not contain all of the original raw data or the complete database itself.

## Reproducibility

This database was created using data obtained via an API key to connect to the CTT servers, therefore the raw data has not been included. The code in this respository was written at the time of creating the database, up to date guidance for how to do this can be found at the [CTT GitHub](https://github.com/cellular-tracking-technologies) or on their [online tutorial](https://cellular-tracking-technologies.github.io/). 

This repository contains code written in:

- **SQL** – for database creation, queries and data management using PostgreSQL.
- **R** – for data processing and analysis.
- **Python** – for data processing and supporting workflows.

The code was developed using PostgreSQL, R and Python. Package and library dependencies are documented within the relevant scripts.

Database connection details, credentials and other sensitive information should be configured locally and are not included in this repository.

The scripts should be run in the appropriate order to create the database structure and import the relevant data:

- `01_download_data_ctt.R`
- `02_schema_backup.sql`
- `03_set_node_tables.sql` (This script is to make the appropriate tables to add any edited node data, the subfolder <mark style="background-color: lightyellow">04_node_timestamp_correction</mark> should follow next.)
- <mark style="background-color: lightyellow">04_node_timestamp_correction</mark>
  - <mark style="background-color: lightyellow">04_01_data_wrangling</mark>
    - `04_01_01_node_data_processing.ipynb`
    - `04_01_02_station_data_processing.ipynb`
  - <mark style="background-color: lightyellow">04_02_proof</mark>
    - <mark style="background-color: lightyellow">04_02_01_window_size</mark>
      - `04_02_01_01_window_size_030.ipynb` (This script was repeated with window sizes of 30 minutes, 1 hour and 2 hours, and tested different cut off values for KL divergence scores.)
    - <mark style="background-color: lightyellow">04_02_02_simulation</mark>
      - `04_02_02_01_simulation_BatHouse_random_sample.ipynb`
      - `04_02_02_02_simulation_BatHouse_seed_06.py`
      - `04_02_02_03_simulation_Huxbear_random_sample.ipynb`
      - `04_02_02_04_simulation_Huxbear_seed_04.py`
      - `04_02_02_05_simulation_Olchard_A_random_sample.ipynb`
      - `04_02_02_06_simulation_Olchard_A_seed_08.py`
      - `04_02_02_07_simulation_Olchard_C_random_sample.ipynb`
      - `04_02_02_08_simulation_Olchard_C_seed_02.py`
      - `04_02_02_09_simulation_plot_results.ipynb`
      - `04_02_02_10_simulation_export_results.ipynb`
  - <mark style="background-color: lightyellow">04_03_correction</mark>
    - `04_03_01_correction_BatHouse_30min.py`
    - `04_03_02_correction_Olchard_30min.py`
    - `04_03_03_correction_Sandygate_30min.py`
    - `04_03_04_correction_HighlandPark_30min.py`
    - `04_03_05_export_results.ipynb`
    - `04_03_06_manual_edits.ipynb`
- `05_add_corrected_node_data.sql`
- `06_clean_data.sql`
- `07_import_deployment_csv.sql`
- `08_join_station_deployment_info.sql`
- `09_create_test_tag_table.sql`
- `10_create_bat_data_table.sql`
- `11_sun_times_table.R`

## Related research

This database supported the research undertaken as part of my PhD at the University of Sussex. My thesis, "Monitoring the winter activity of the greater horseshoe bat, *Rhinolophus ferrumequinum*, using an Automated Radio Telemetry System", is available at [the University of Sussex Figshare](https://hdl.handle.net/10779/uos.34094334).

The code used to analyse individual research chapters is available in separate repositories, where applicable.
- [Chapter 2](https://github.com/kallan96/GHS_winter_activity) 

## Citation

If you use this code, please cite the repository:

Allan, K. (2026). UK_Bats_database: Code for the construction of the PhD bat research database [Computer software]. GitHub. https://github.com/kallan96/UK_Bats_database

## Licence

This repository is licensed under the MIT Licence. See the LICENSE file for details.

## Author

Dr Katie Allan  
University of Sussex
