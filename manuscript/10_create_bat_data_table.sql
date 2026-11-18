-----------------------------
--
-- Script name: 10_create_bat_data_tables.sql
--
-- Purpose of script: This script is to create data tables of the tags used on the bats in the study.
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
-- Notes: Ensure survey record data has been imported from the csv.
--
-----------------------------
-- create a new bat table
CREATE TABLE public.bat_data AS
SELECT public.joined_station_data.*, public.bat_tags.bat_name,  public.bat_tags.ring_no,  public.bat_tags.location as capture_site 
FROM public.joined_station_data
JOIN public.bat_tags 
ON public.joined_station_data.tag_id = public.bat_tags.tag_id
AND public.joined_station_data.time >= public.bat_tags.time
ORDER BY public.joined_station_data.time;

--create new table of bat_summary_data
CREATE TABLE public.bat_summary_data AS
SELECT DISTINCT on (tag_id, time, station_id, tag_rssi) public.bat_data.* 
FROM public.bat_data
WHERE node_id IS NULL
ORDER BY tag_id, time, station_id, tag_rssi DESC;

-- insert data from nodes into table
INSERT INTO public.bat_summary_data 
SELECT DISTINCT on (tag_id, time, node_id, tag_rssi) public.bat_data.*
FROM public.bat_data
WHERE node_id IS NOT NULL
ORDER BY tag_id, time, node_id, tag_rssi DESC;
