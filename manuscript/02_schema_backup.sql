-----------------------------
--
-- Script name: 02_schema_backup.sql
--
-- Purpose of script: This script is to backup the data that was downloaded from the CTT servers into a separate schema in PostgreSQL.
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
-- Notes: The 'raw' schema should not be used for any subsequent data processing or analyses, it is for backup purposes only.
--
-----------------------------
--create new raw schema
CREATE SCHEMA raw;

--create and copy raw table to raw schema as backup
CREATE TABLE raw.raw (LIKE public.raw INCLUDING ALL);

INSERT INTO raw.raw
SELECT * 
FROM public.raw;

--create and copy nodes table to raw schema as backup
CREATE TABLE raw.nodes (LIKE public.nodes INCLUDING ALL);

INSERT INTO raw.nodes
SELECT * 
FROM public.nodes;

--create and copy node_health table to raw schema as backup
CREATE TABLE raw.node_health (LIKE public.node_health INCLUDING ALL);

INSERT INTO raw.node_health
SELECT * 
FROM public.node_health;

--create and copy gps table to raw schema as backup
CREATE TABLE raw.gps (LIKE public.gps INCLUDING ALL);

INSERT INTO raw.gps
SELECT * 
FROM public.gps;

--create and copy data_file table to raw schema as backup
CREATE TABLE raw.data_file (LIKE public.data_file INCLUDING ALL);

INSERT INTO raw.data_file
SELECT * 
FROM public.data_file;

--create and copy ctt_project_station table to raw schema as backup
CREATE TABLE raw.ctt_project_station (LIKE public.ctt_project_station INCLUDING ALL);

INSERT INTO raw.ctt_project_station
SELECT * 
FROM public.ctt_project_station;

--create and copy ctt_project table to raw schema as backup
CREATE TABLE raw.ctt_project (LIKE public.ctt_project INCLUDING ALL);

INSERT INTO raw.ctt_project
SELECT * 
FROM public.ctt_project;