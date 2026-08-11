-----------------------------
--
-- Script name: 07_import_deployment_csv.sql
--
-- Purpose of script: This script is to import data from radio station deployments and bat trapping survey data.
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
-- Notes: Change 'path_to_folder' to appropriate folder paths.
--
-----------------------------
-- create table of bat tags
CREATE TABLE public.bat_tags(
id SERIAL PRIMARY KEY,
bat_name text,
tag_id text,
location text,
survey_type text,
time timestamp with time zone NOT NULL,
surveyors text,
handler text,
species text,
ring_no text,
ring_new text,
forearm decimal,
sex text,
repro text,
false_nips text,
age text,
weight decimal
);

-- copy data from .csv file
\copy public.bat_tags(bat_name,tag_id,location,survey_type,time,surveyors,handler,species,ring_no,ring_new,forearm,sex,repro,false_nips,age,weight) FROM 'path_to_folder\bat_data.csv' DELIMITER ‘,’ NULL AS 'NA' CSV HEADER;

-- create table of station history
CREATE TABLE public.station_history(
id SERIAL PRIMARY KEY,
station_ID text,
Type text,
Latitude decimal,
Longitude decimal,
Deploy timestamp with time zone NOT NULL,
Remove timestamp with time zone,
Location text,
Software text
);

-- copy data from .csv file
\copy public.station_history(station_ID,Type,Latitude,Longitude,Deploy,Remove,Location,Software) FROM 'path_to_folder\StationLocationsHistory.csv' DELIMITER ‘,’ NULL AS 'NA' CSV HEADER;