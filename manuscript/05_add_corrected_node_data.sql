-----------------------------
--
-- Script name: 05_add_corrected_node_data.sql
--
-- Purpose of script: This script is to combine the corrected node timestamp data into the main database.
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
-- Notes: Python scripts for editing the node timestamps must be run before this script, which can be found in the subfolder '04_node_timestamp_correction'.
--
-----------------------------
--combine data from raw and node tables into one - add KL Divergence data first
INSERT INTO public.all_data
SELECT * FROM public.kl_divergence_node_data;

--then add manual data
INSERT INTO public.all_data
SELECT * FROM public.manual_edited_node_data;
