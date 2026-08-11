-----------------------------
--
-- Script name: 06_clean_data.sql
--
-- Purpose of script: This script is to clean node and station data.
--
-- Author: Dr Katie Allan
--
-- Date Created: 2022-07-10
--
-- Email: katie.allan@sussex.ac.uk
--
-- License: 
--
-----------------------------
--
-- Notes: Node names will be recoded and duplicates will be removed.
--
-----------------------------
-- create new table of raw data
CREATE TABLE public.clean_data AS
SELECT DISTINCT 
radio_id, tag_id, node_id, tag_rssi, validated, time, station_id, method, data_size, median_error_seconds, max_error_seconds
FROM
public.all_data;

-- count the number of rows in the table
--SELECT count(*) FROM public.clean_data;

-- check the unique node_id values;
--SELECT DISTINCT node_id FROM public.clean_data;

-- recode node names to match correct values
UPDATE public.clean_data 
SET node_id = 
CASE node_id
WHEN '327D6B' THEN '327d6b'
WHEN '325B22' THEN '325b22'
WHEN '3288AE' THEN '3288ae'
WHEN '3289F3' THEN '3289f3'
WHEN '3289F1' THEN '3289f1'
WHEN '32800C' THEN '32800c'
WHEN '328F57' THEN '328f57'
WHEN '32B6E0' THEN '32b6e0'
WHEN '3292C8' THEN '3292c8'
WHEN '37807E' THEN '37807e'
WHEN '37807' THEN '37807e'
WHEN '37792F' THEN '37792f'
WHEN '37792' THEN '37792f'
WHEN '376F37' THEN '376f37'
WHEN '376A2B' THEN '376a2b'
WHEN '37920B' THEN '37920b'
WHEN '3795D0' THEN '3795d0'
WHEN '376ADF' THEN '376adf'
WHEN '3750B3' THEN '3750b3'
WHEN '379F1A' THEN '379f1a'
WHEN '3781A5' THEN '3781a5'
ELSE node_id
END;

-- check the recode worked;
--SELECT DISTINCT node_id FROM public.clean_data;

-- create new table of only node's
-- CREATE VIEW
CREATE TABLE z_clean_node_data AS
SELECT DISTINCT on (node_id, tag_id, tag_rssi, time) clean_data.* 
FROM public.clean_data
WHERE node_id IN (SELECT DISTINCT station_id 
FROM public.station_history
WHERE type = 'Node' ORDER BY station_id)
ORDER BY node_id;

-- create new table of only station's
CREATE TABLE z_clean_station_data AS
SELECT DISTINCT on (station_id, radio_id, tag_id, tag_rssi, time) clean_data.* 
FROM public.clean_data
WHERE station_id IN (SELECT DISTINCT station_id
FROM public.station_history
WHERE type = 'Station' ORDER BY station_id)
AND node_id IS NULL
ORDER BY station_id;

--remove all records from clean_data table
DELETE FROM public.clean_data;

-- insert data from node and stations into single table
INSERT INTO public.clean_data 
SELECT * FROM public.z_clean_station_data 
UNION 
Select * FROM public.z_clean_node_data;

-- count the number of rows in the final table
SELECT count(*) FROM public.clean_data;

-- remove the node and station tables
DROP TABLE public.z_clean_station_data, public.z_clean_node_data;