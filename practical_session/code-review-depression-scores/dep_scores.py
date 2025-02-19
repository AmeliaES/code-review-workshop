# Calculate depression scores and total number of depressive episodes

import pandas as pd
import numpy as np

# Calculate depression scores for each age group

mfq_t1Vars = ["fddp110", "fddp112", "fddp113", "fddp114", "fddp115", "fddp116", "fddp118", "fddp119", "fddp121", "fddp122", "fddp123", "fddp124", "fddp125"]
mfq_t2Vars = ["ff6500", "ff6502", "ff6503", "ff6504", "ff6505", "ff6506", "ff6508", "ff6509", "ff6511", "ff6512", "ff6513", "ff6514", "ff6515"]
mfq_t3Vars = ["fg7210", "fg7212", "fg7213", "fg7214", "fg7215", "fg7216", "fg7218", "fg7219", "fg7221", "fg7222", "fg7223", "fg7224", "fg7225"]
mfq_t4Vars = ["ccs4500", "ccs4502", "ccs4503", "ccs4504", "ccs4505", "ccs4506", "ccs4508", "ccs4509", "ccs4511", "ccs4512", "ccs4513", "ccs4514", "ccs4515"]
mfq_t5Vars = ["CCXD900", "CCXD902", "CCXD903", "CCXD904", "CCXD905", "CCXD906", "CCXD908", "CCXD909", "CCXD911", "CCXD912", "CCXD913", "CCXD914", "CCXD915"]
mfq_t6Vars = ["cct2700", "cct2701", "cct2702", "cct2703", "cct2704", "cct2705", "cct2706", "cct2707", "cct2708", "cct2709", "cct2710", "cct2711", "cct2712"]
mfq_t7Vars = ["YPA2000", "YPA2010", "YPA2020", "YPA2030", "YPA2040", "YPA2050", "YPA2060", "YPA2070", "YPA2080", "YPA2090", "YPA2100", "YPA2110", "YPA2120"]

# coded differently: 1 should be 0, 2 should be 1 and 3 should be 2.
mfq_t8Vars = ["YPB5000", "YPB5010", "YPB5030", "YPB5040", "YPB5050", "YPB5060", "YPB5080", "YPB5090", "YPB5100", "YPB5120", "YPB5130", "YPB5150", "YPB5170"]
mfq_t9Vars = ["YPC1650", "YPC1651", "YPC1653", "YPC1654", "YPC1655", "YPC1656", "YPC1658", "YPC1659", "YPC1660", "YPC1662", "YPC1663", "YPC1665", "YPC1667"]

# coded correctly:
mfq_t10Vars = ["YPE4080", "YPE4082", "YPE4083", "YPE4084", "YPE4085", "YPE4086", "YPE4088", "YPE4089", "YPE4091", "YPE4092", "YPE4093", "YPE4094", "YPE4095"]
mfq_t11Vars = ["covid4yp_4050", "covid4yp_4051", "covid4yp_4052", "covid4yp_4053", "covid4yp_4054", "covid4yp_4055", "covid4yp_4056", "covid4yp_4057", "covid4yp_4058", "covid4yp_4059", "covid4yp_4060", "covid4yp_4061", "covid4yp_4062"]

mfqAllVars = {
    "mfq_t01": mfq_t1Vars, "mfq_t02": mfq_t2Vars, "mfq_t03": mfq_t3Vars,
    "mfq_t04": mfq_t4Vars, "mfq_t05": mfq_t5Vars, "mfq_t06": mfq_t6Vars,
    "mfq_t07": mfq_t7Vars
}

# Check if there are any participants where consent is not given for the depression questions:
consent_check = {}
for timepoint in [mfq_t1Vars, mfq_t2Vars, mfq_t3Vars, mfq_t4Vars, mfq_t5Vars, mfq_t6Vars, mfq_t7Vars, mfq_t8Vars, mfq_t9Vars, mfq_t10Vars, mfq_t11Vars]:
    consent_check[timepoint] = {var: (data[var] == -9999).sum() for var in timepoint}

# No, anyone who has not given consent is already not in our data

# Calculate smfq scores:
smfq = {}
for key, vars in mfqAllVars.items():
    smfq[key] = data[vars].apply(pd.to_numeric, errors='coerce').replace({3: 0, 2: 1, 1: 2}).sum(axis=1)

dataSmfq = pd.concat([data, pd.DataFrame(smfq)], axis=1)

# Reverse score of *_t8 and *_t9
smfq_t8 = data[mfq_t8Vars].apply(pd.to_numeric, errors='coerce').replace({3: 2, 2: 1, 1: 0}).sum(axis=1)
smfq_t9 = data[mfq_t9Vars].apply(pd.to_numeric, errors='coerce').replace({3: 2, 2: 1, 1: 0}).sum(axis=1)

dataSmfq = pd.concat([dataSmfq, smfq_t8.rename("mfq_t08"), smfq_t9.rename("mfq_t09")], axis=1)

# Correct score
smfq_t10 = data[mfq_t10Vars].apply(pd.to_numeric, errors='coerce').replace({2: 2, 1: 1, 0: 0}).sum(axis=1)
smfq_t11 = data[mfq_t11Vars].apply(pd.to_numeric, errors='coerce').replace({2: 2, 1: 1, 0: 0}).sum(axis=1)

dataSmfq = pd.concat([dataSmfq, smfq_t10.rename("mfq_t10"), smfq_t11.rename("mfq_t11")], axis=1)

# Calculate number of depression episodes
# (SMFQ >= 11) Turner et al. 2014 - https://doi.org/10.1037/a0036572
dataSmfq['dep_episodes'] = (dataSmfq[list(mfqAllVars.keys())] >= 11).sum(axis=1)

# some of those 0s should be NA though for people that didn't attend ANY appointments 
# as it's a bit misleading
dataSmfq.loc[(dataSmfq[list(mfqAllVars.keys())].isna().sum(axis=1) == len(mfqAllVars)), 'dep_episodes'] = np.nan

# Also add col of number of appointments participant attended
dataSmfq['dep_appts'] = dataSmfq[list(mfqAllVars.keys())].notna().sum(axis=1)

# Calculate n, mean, sd, median and IQR and % of people with score >= 11
timePoint = ["mfq_t01", "mfq_t02", "mfq_t03", "mfq_t04", "mfq_t05", "mfq_t06", "mfq_t07", "mfq_t08", "mfq_t09", "mfq_t10", "mfq_t11"]
occasions = [1, 3, 5, 7, 8, 9, 10, 11, 12, 14, 16]

stats = []
for i, timepoint in enumerate(timePoint):
    occasion = occasions[i]
    sample_size = dataSmfq[timepoint].notna().sum()
    responses = dataSmfq[timepoint].dropna()
    smfq_mean = responses.mean()
    smfq_sd = responses.std()
    smfq_median = responses.median()
    smfq_iqr = responses.quantile(0.75) - responses.quantile(0.25)
    above_threshold = (responses >= 11).sum() / sample_size * 100
    stats.append([occasion, sample_size, smfq_mean, smfq_sd, smfq_median, smfq_iqr, above_threshold])

SmfqDescStatsAll = pd.DataFrame(stats, columns=["Occasion", "Sample_Size", "SMFQ_Mean", "SMFQ_SD", "SMFQ_Median", "SMFQ_IQR", "Above_Threshold"])
print(SmfqDescStatsAll)
SmfqDescStatsAll.to_csv("Output/SMFQ_Descriptive_Statistics.csv", index=False)