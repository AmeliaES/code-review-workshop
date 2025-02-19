# Cluster participants by their WBC, CRP and GlycA data
# investigate if some clusters have more of some symptoms or diagnoses than others

# Follow this: https://programminghistorian.org/en/lessons/clustering-with-scikit-learn-in-python

# -----------------------------------------
# Import libraries
library(tidyverse)
library(readr)
library(dplyr)
library(ggplot2)
library(cluster)
library(factoextra)
library(caret)
library(reshape2)

# Set seed for reproducibility
set.seed(100)

# -----------------------------------------
# Read in file with UKB fields:
UKB_fields <- read_delim('data/UKB_fields.txt', delim = " ")
head(UKB_fields)

# Get list of field IDs from first column of UKB_fields
f_ids <- UKB_fields$field_id

# include "f.eid" at the start of this list as we always want this column
f_ids <- c("f.eid", f_ids)

print(f_ids)

# -----------------------------------------
# Read in and tidy data of bloods 
dataBloods <- readRDS('data/2019-05-biomarkers-ukb29707_BiologicalSamples.rds')
head(dataBloods)
str(dataBloods)

# Subset columns to those in f_ids
dataBloods <- dataBloods %>% select(all_of(f_ids))
head(dataBloods)
str(dataBloods)

# Rename columns based on UKB descriptions
colnames(dataBloods) <- UKB_fields$field[match(colnames(dataBloods), UKB_fields$field_id)]
head(dataBloods)
str(dataBloods) # 468594 not missing for CRP

# Remove people with CRP >= 10 mg/L. First change them to 0, and then NA. This keeps the type numeric.
dataBloods <- dataBloods %>% mutate(CRP = ifelse(CRP >= 10, NA, CRP))

# Check that the max is below 10
max(dataBloods$CRP, na.rm = TRUE)
str(dataBloods) # 449141 not missing for CRP

# Remove NA values, ie. subset dataframe to complete cases only
dataBloods <- dataBloods %>% drop_na()
head(dataBloods)
str(dataBloods) # 436,864 not missing for all cols

# -----------------------------------------
# Read in and tidy data of GlycA measures in subset of sample (this file is slow to load)
dataGlycA <- read_delim("data/NMRMetabolomics.tsv", delim = "\t")

dim(dataGlycA)
str(dataGlycA)
head(dataGlycA)
colnames(dataGlycA)
dataGlycA <- dataGlycA %>% rename(GlycA = `f.23480.0.0`)
dataGlycA$GlycA

dataGlycA <- dataGlycA %>% drop_na()
head(dataGlycA)
str(dataGlycA)

dataBloods <- merge(dataBloods, dataGlycA %>% select(f.eid, GlycA), by = 'f.eid')

# -----------------------------------------
# Read in and tidy up diagnosis data (this is a table made in "../PRS_project/Blood_marker_regression/Scripts/psych_diagnosis.R") 
# - come back to later and replicate that script here - probably get bigger N (also means we aren't reading a file in from a different project)
dataPsych <- readRDS('../PRS_project/Blood_marker_regression/target_data_files/psych_diagnosis.rds')

head(dataPsych)

# Create a new col to combine self diagnosed OR ICD-10 diagnosis 
dataPsych <- dataPsych %>%
  mutate(MDD = ifelse(MDD_self == 1 | MDD_ICD10 == 1, 1, 0),
         BD = ifelse(BD_self == 1 | BD_ICD10 == 1, 1, 0),
         SCZ = ifelse(SCZ_self == 1 | SCZ_ICD10 == 1, 1, 0))

head(dataPsych)