# Code review of `cluster_ukb.py` script

## Message to reviewer:

> Hi, please can you review `cluster_ukb.py` (or `cluster_ukb.R`). I got as far as loading the UK Biobank data, cleaning it, and creating new columns to combine self-diagnosed and ICD-10 diagnoses. The script aims to eventually cluster participants based on their WBC (White Blood Cell count), CRP (C-Reactive Protein), and GlycA (Glycoprotein Acetylation) data to investigate if there is an immune-related subtype of depression. 

> The UK Biobank is a large-scale biomedical database and research resource containing in-depth genetic and health information from half a million UK participants. ICD-10 is the International Classification of Diseases, which is a medical classification list by the World Health Organization (WHO). I use it in this script to define some mental health conditions.

> A quick walk through of the code and what it does:

* Load in libraries and set up the environment.
* Read in the UK Biobank fields and extract the relevant field IDs. 
  * The UK Biobank dataset contains numerous fields, each representing different types of data collected from participants, such as demographic information, health records, and various biomarkers. The field IDs are unique identifiers for these fields. In this step, we read a file that lists these field IDs and descriptions, and extract the IDs that are relevant to our analysis.
* Load and tidy the blood biomarkers data, including handling missing values and renaming columns.
  * This involves reading the blood biomarker data, which includes measurements like WBC and CRP, and cleaning it by handling missing values and renaming columns to more descriptive names based on the UK Biobank field descriptions.
* Load and tidy the GlycA measures data, merging it with the blood biomarkers data.
  * GlycA is another inflammatory biomarker measured in a subset of the participants. This step involves reading the GlycA data, cleaning it, and merging it with the previously cleaned blood biomarkers data.
* Load and tidy the diagnosis data, creating new columns to combine self-diagnosed and ICD-10 diagnoses.
  * This step involves reading diagnosis data, which includes both self-reported diagnoses and diagnoses coded using ICD-10. We create new columns to combine these two sources of diagnosis information for conditions like Major Depressive Disorder (MDD) and Bipolar Disorder (BD).

> Many thanks for your time, any feedback or suggested changes would be much appreciated.