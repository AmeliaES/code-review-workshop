# Cluster participants by their WBC, CRP and GlycA data
# investigate if some clusters have more of some symptoms or diagnoses than others

# Follow this: https://programminghistorian.org/en/lessons/clustering-with-scikit-learn-in-python

# -----------------------------------------
# Import modules
import tarfile
import urllib
import os

import pyreadr

from sklearn.preprocessing import StandardScaler as SS # z-score standardization 
from sklearn.cluster import KMeans, DBSCAN # clustering algorithms
from sklearn.decomposition import PCA # dimensionality reduction
from sklearn.metrics import silhouette_score # used as a metric to evaluate the cohesion in a cluster
from sklearn.neighbors import NearestNeighbors # for selecting the optimal eps value when using DBSCAN
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 100)
pd.options.display.float_format = '{:.2f}'.format # Turns of scientific notation for float numbers

import researchpy as rp

import random
random.seed(100)

# plotting libraries
import matplotlib.pyplot as plt

from scipy import stats

import seaborn as sns
from yellowbrick.cluster import SilhouetteVisualizer

# Check current working directory (should be correct if running from within the conda environment)
os.getcwd()

# -----------------------------------------
# Read in file with UKB fields:
UKB_fields = pd.read_fwf('data/UKB_fields.txt', sep=" ")
UKB_fields.head()

# Get list of field IDs from first column of UKB_fields
f_ids = UKB_fields['field_id'].tolist()

# include "f.eid" at the start of this list as we always want this column
f_ids.insert(0, "f.eid")

print(f_ids)

# -----------------------------------------
# Read in and tidy data of bloods 
dataBloods = pyreadr.read_r('data/2019-05-biomarkers-ukb29707_BiologicalSamples.rds')[None] # also works for RData
dataBloods.head()
dataBloods.info()

# Subset columns to those in f_ids
print(dataBloods.columns.intersection(f_ids))

dataBloods = dataBloods[dataBloods.columns.intersection(f_ids)]
dataBloods.head()
dataBloods.info()

# Rename columns based on UKB descriptions
dataBloods.rename(columns=UKB_fields.set_index('field_id')['field'], inplace = True)
dataBloods.head()
dataBloods.info() # 468594 not missing for CRP

# Remove people with CRP >= 10 mg/L. First change them to 0, and then NA. This keeps the type numeric.
dataBloods.loc[dataBloods['"CRP"'] >= 10, '"CRP"'] = 0
dataBloods['"CRP"'].replace(0, np.NaN, inplace = True)

# Check that the max is below 10
dataBloods['"CRP"'].max()
dataBloods.info() # 449141 not missing for CRP

# Remove NA values, ie. subset dataframe to complete cases only
dataBloods.dropna(axis = 0, how = 'any', inplace = True)
dataBloods.head()
dataBloods.info() # 436,864 not missing for all cols

# -----------------------------------------
# Read in and tidy data of GlycA measures in subset of sample (this file is slow to load)
dataGlycA = pd.read_csv("data/NMRMetabolomics.tsv", sep = "\t")

dataGlycA.shape
dataGlycA.info()
dataGlycA.head()
dataGlycA.columns
dataGlycA["f.23480.0.0"]
dataGlycA.rename({"f.23480.0.0" : "GlycA"}, axis = 1, inplace = True)
dataGlycA["GlycA"]

dataGlycA.dropna(axis = 0, how = 'any', inplace = True)
dataGlycA.head()
dataGlycA.info()

dataBloods = pd.merge(dataBloods, dataGlycA[['f.eid', 'GlycA']], on='f.eid')

# -----------------------------------------
# Read in and tidy up diagnosis data (this is a table made in "../PRS_project/Blood_marker_regression/Scripts/psych_diagnosis.R") 
# - come back to later and replicate that script here - probably get bigger N (also means we aren't reading a file in from a different project)
dataPsych = pyreadr.read_r('../PRS_project/Blood_marker_regression/target_data_files/psych_diagnosis.rds')[None]

dataPsych.head()

# Create a new col to combine self diagnosed OR ICD-10 diagnosis 
def MDDConditions(x):
    if (x['MDD_self'] == 1) or (x['MDD_ICD10'] == 1):
        return 1
    else:
        return 0

dataPsych['MDD'] = dataPsych.apply(MDDConditions, axis = 1)

def BDConditions(x):
    if (x['BD_self'] == 1) or (x['BD_ICD10'] == 1):
        return 1
    else:
        return 0

dataPsych['BD'] = dataPsych.apply(BDConditions, axis = 1)

def SCZConditions(x):
    if (x['SCZ_self'] == 1) or (x['SCZ_ICD10'] == 1):
        return 1
    else:
        return 0

dataPsych['SCZ'] = dataPsych.apply(SCZConditions, axis = 1)

dataPsych.head()

