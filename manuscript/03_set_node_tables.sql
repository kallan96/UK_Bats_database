-----------------------------
--
-- Script name: 03_set_node_tables.sql
--
-- Purpose of script: This script is to set up the tables that are required for correcting the node timestamps that were corrupted.
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
-- Notes: Python scripts for editing the node timestamps should be run next, found in the subfolder '04_node_timestamp_correction'.
--
-----------------------------
--create node table in format of clean data
CREATE TABLE public.manual_edited_node_data (LIKE public.raw INCLUDING ALL);

--create new columns needed for edited node data
ALTER TABLE public.manual_edited_node_data
ADD COLUMN method text,
ADD COLUMN data_size integer,
ADD COLUMN median_error_seconds integer,
ADD COLUMN max_error_seconds integer;


--create node table in format of clean data
CREATE TABLE public.kl_divergence_node_data (LIKE public.raw INCLUDING ALL);

--create new columns needed for edited node data
ALTER TABLE public.kl_divergence_node_data
ADD COLUMN method text,
ADD COLUMN data_size integer,
ADD COLUMN median_error_seconds integer,
ADD COLUMN max_error_seconds integer;


-- create new table for joined data
SELECT * INTO public.all_data FROM public.raw;


--create new columns needed to match edited node data
ALTER TABLE public.all_data
ADD COLUMN method text,
ADD COLUMN data_size integer,
ADD COLUMN median_error_seconds integer,
ADD COLUMN max_error_seconds integer;

--update new columns to have values
UPDATE public.all_data
SET method = 'ctt',
    data_size = NULL,
    median_error_seconds = NULL,
    max_error_seconds = NULL;

