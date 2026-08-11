-----------------------------
--
-- Script name: 09_create_test_tag_tables.sql
--
-- Purpose of script: This script is to create data tables of the tags used in calibration and testing.
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
-- Notes: 'elephant' refers to the large tag used to test if receivers were working; 'old' refers to the first tag design that was used in initial trials' and 'new' refers to the final tag designt that was used in the study.
--
-----------------------------
--create table of test tags
CREATE TABLE public.test_tags(
   tag_id text NOT NULL,
   tag_type text,
   PRIMARY KEY (tag_id)
);

--add data to the test tag table
INSERT INTO public.test_tags(tag_id, tag_type) 
VALUES ('55331961', 'elephant'),
('344C2D78', 'old'),
('66665255', 'old'),
('34551E19', 'old'),
('3334612D', 'old'),
('2D4C4C2A', 'old'),
('78334C61', 'old'),
('61525507', 'new'),
('66334C2A', 'new'),
('4B551E4B', 'new'),
('5561554C', 'new'),
('78780778', 'new');

-- create a test_tag_data table
CREATE TABLE public.test_tag_data AS
SELECT * FROM public.joined_station_data
WHERE tag_id in (SELECT 
DISTINCT tag_id 
FROM public.test_tags);

--create elephant tag table
CREATE TABLE public.elephant_tag_data AS
SELECT * FROM public.joined_station_data
WHERE tag_id in (SELECT 
DISTINCT tag_id 
FROM public.test_tags
WHERE tag_type = 'elephant');

--create old tag table
CREATE TABLE public.old_tag_data AS
SELECT * FROM public.joined_station_data
WHERE tag_id in (SELECT 
DISTINCT tag_id 
FROM public.test_tags
WHERE tag_type = 'old');

--create new tag table
CREATE TABLE public.new_tag_data AS
SELECT * FROM public.joined_station_data
WHERE tag_id in (SELECT 
DISTINCT tag_id 
FROM public.test_tags
WHERE tag_type = 'new');
