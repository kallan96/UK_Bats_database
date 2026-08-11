## ---------------------------
##
## Script name: 01_download_data_ctt.R
##
## Purpose of script: This script is to download data from the CTT servers via API. This is the code that I used for the initial download with credentials removed. Please follow the updated tutorial from the celltracktech R package, available here: https://github.com/cellular-tracking-technologies/celltracktech 
##
## Author: Dr Katie Allan
##
## Date Created: 2022-07-10
##
## Email: katie.allan@sussex.ac.uk
##
## License: 
##
## ---------------------------
##
## Notes: PostgreSQL must be installed and appropriate libraries installed prior to running this script. It is now recommended to create a '.env' file with required passwords and credentials, please see available tutorial.
##
## ---------------------------
## load required packages
library(celltracktech)
library(DBI)
library(RPostgres)

start <- Sys.time()

####Set credentials####
my_token <- "API_key" #CTT server API key
outpath <- "set_data_directory" #folder outpath of data directory
db_name <- "set_postgresql_name" #postgreSQL database name
myproject <- "set_project_name" #CTT project name
conn <- dbConnect(RPostgres::Postgres(), dbname=db_name) #set up connection to postgreSQL database
################

print(paste0("Get Data from CTT server and download to computer."))
get_my_data(my_token, 
            outpath, 
            conn, 
            myproject)

print(paste0("Update data into PostgreSQL database."))
update_db(conn, 
          outpath, 
          myproject, 
          TRUE)

print(paste0("Import Node data from local files."))
import_node_data(conn, 
                 outpath, 
                 myproject)

print(paste0("Clean Up PostgreSQL database"))
db_cleanup(conn)

#disconnect from PostgreSQL database
dbDisconnect(conn)

time_elapse <- Sys.time() - start
print(time_elapse)

