-----------------------------
--
-- Script name: 08_join_station_deployment_info.sql
--
-- Purpose of script: This script is to join the station location data to the appropriate detection data based on the receiver ID and deployment history.
--
-- Author: Dr. Katie Allan
--
-- Date Created: 2022-07-10
--
-- Email: katie.allan@sussex.ac.uk
--
-- License: 
--
-----------------------------
--
-- Notes: Ensure station deployment history has been imported from the csv.
--
-----------------------------
-- create a new station history table
CREATE TABLE public.z_rec_history_clean AS
SELECT * FROM public.station_history;

-- set NA columns to current system time in new table
UPDATE public.z_rec_history_clean 
SET Remove = (SELECT CURRENT_TIMESTAMP)
WHERE Remove IS NULL;

-- check NA change worked
SELECT * FROM public.z_rec_history_clean WHERE Remove IS NULL;

--create new table of only station's
CREATE TABLE public.z_clean_station_data AS
SELECT DISTINCT * FROM public.clean_data
WHERE 
node_id IS NULL;

--join the tables together by ID and deploy/remove time
CREATE TABLE public.z_filter_step AS
SELECT public.z_clean_station_data.*, public.z_rec_history_clean.latitude, public.z_rec_history_clean.longitude, public.z_rec_history_clean.deploy, public.z_rec_history_clean.remove, public.z_rec_history_clean.location, public.z_rec_history_clean.software
FROM public.z_clean_station_data
JOIN public.z_rec_history_clean
ON public.z_clean_station_data.station_id = public.z_rec_history_clean.station_id
AND public.z_clean_station_data.time >= public.z_rec_history_clean.Deploy
AND public.z_clean_station_data.time <= public.z_rec_history_clean.Remove;

-- create new table for joined data
CREATE TABLE public.joined_station_data AS
SELECT * FROM public.z_filter_step;

-- drop filter step table
DROP TABLE public.z_filter_step;

--create new table of only nodes
CREATE TABLE public.z_clean_node_data AS
SELECT DISTINCT * FROM public.clean_data
WHERE 
node_id IS NOT NULL;

--join the tables together by ID and deploy/remove time
CREATE TABLE public.z_filter_step AS
SELECT public.z_clean_node_data.*, public.z_rec_history_clean.latitude, public.z_rec_history_clean.longitude, public.z_rec_history_clean.deploy, public.z_rec_history_clean.remove, public.z_rec_history_clean.location, public.z_rec_history_clean.software
FROM public.z_clean_node_data
JOIN public.z_rec_history_clean
ON public.z_clean_node_data.node_id = public.z_rec_history_clean.station_id
AND public.z_clean_node_data.time >= public.z_rec_history_clean.Deploy
AND public.z_clean_node_data.time <= public.z_rec_history_clean.Remove;

-- insert data from stations into single table
INSERT INTO public.joined_station_data SELECT * FROM public.z_filter_step;

-- count the number of records in the new dataframe
SELECT COUNT(*) FROM public.joined_station_data;

-- remove unused tables
DROP TABLE public.z_clean_node_data, public.z_clean_station_data, public.z_filter_step, public.z_rec_history_clean;