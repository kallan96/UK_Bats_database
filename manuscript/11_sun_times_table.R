## ---------------------------
##
## Script name: 11_sun_times_table.R
##
## Purpose of script: This script is to calculate the sunrise and sunset times of the study period and to make a postgres table and csv.
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
## Notes: Set credentials for postgres databse.
##
## ---------------------------
## load required packages
library(RPostgres)
library(suncalc)
library(tidyverse)



#Connect to PostgreSQL database ####
db_name <- "UK_Bats"
conn <- dbConnect(RPostgres::Postgres(), dbname=db_name, user='user', password='password')



#Calculate sun data ####
#Get sunlight information
sunlight_times <- getSunlightTimes(date = seq(from = as.Date("2021-09-13"), by = 1, to = as.Date("2024-01-25")), #dates of the study
                                   keep = c("sunrise", "sunriseEnd", "sunsetStart", "sunset", "dusk", "night", "nadir", "nightEnd", "dawn"), 
                                   lat = 50.590305, lon = -3.612610, #lat long is centre of site
                                   tz = "UTC")

#Raname date column
sunlight_times <- rename_at(sunlight_times, "date", ~"Date")



#Write to postgres and csv ####
write.csv(sunlight_times, "data/sunlight_times.csv") 

dbWriteTable(conn = conn, overwrite=TRUE, "sun_data", sunlight_times)
