# Analyse steps data from my FitBit
# Ideas:
# Find out how many steps I do a day on average
# Find out if there's a relationship with time of year, eg. less active in winter more active in summer
# Find out if there's a relationship with the day, eg. weekday or weekend
# Find out when during the day am I usually most active

# Explore missing data, could my results be bias because I don't wear my fitbit at certain times in the day?
# Also need to find out what sets the intervals in data collection when I am wearing my fitbit, as i dont think it's every minute...

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set seaborn theme
sns.set_theme(style="whitegrid")

# Define season colours
season_colours = {
    "Spring": "#a0c73e",
    "Summer": "#e35bd2",
    "Autumn": "#f5ae2c",
    "Winter": "#afd3e3"
}

# Define colours for the night
night_colours = {
    "night": "#6f6278",
    "dawnDusk": "#d9b6b8",
    "day": "#f9fade"
}

# Load data
path_steps = "/Users/aes/GitRepos/fitbitr/Takeout/Fitbit/Global Export Data/"
dates = [f for f in os.listdir(path_steps) if "steps" in f and not f.startswith("2017")]

# Loop over each date to extract the steps data from each file
data_list = []
for date in dates:
    with open(os.path.join(path_steps, date), 'r') as file:
        steps = json.load(file)
        for step in steps:
            data_list.append({
                'dateTime': step['dateTime'],
                'steps': int(step['value'])
            })

data = pd.DataFrame(data_list)

# Extract date and time from the dateTime stamp
data['dateTime'] = pd.to_datetime(data['dateTime'], format="%m/%d/%y %H:%M:%S")
data['date'] = data['dateTime'].dt.date
data['time'] = data['dateTime'].dt.time

# Whats the interval between times?
data['interval'] = data.groupby('date')['dateTime'].diff().dt.total_seconds() / 60

# Plot the interval per steps
plt.figure(figsize=(15, 7.5))
sns.scatterplot(x=data['interval'] / 60, y=data['steps'], alpha=0.5)
plt.xlabel("Time between data collection (hours)")
plt.ylabel("Number of steps")
# plt.savefig("Plots/intervals.png", dpi=300)
plt.close()
plt.show()

# Add up the amount of steps per hour per date
data['hour'] = data['dateTime'].dt.hour + 1
data_by_hour = data.groupby(['date', 'hour'])['steps'].sum().reset_index(name='total_steps')

# Data of steps per day
data_by_day = data_by_hour.groupby('date')['total_steps'].sum().reset_index(name='stepsPerDay')

# Split into weekday/weekend
data_by_hour['day_of_week'] = pd.Categorical(data_by_hour['date'].apply(lambda x: datetime.strptime(str(x), '%Y-%m-%d').strftime('%A')),
                                             categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                             ordered=True)
data_by_hour['weekend'] = np.where(data_by_hour['day_of_week'].isin(['Saturday', 'Sunday']), 'Weekend', 'Weekday')

data_by_day['day_of_week'] = pd.Categorical(data_by_day['date'].apply(lambda x: datetime.strptime(str(x), '%Y-%m-%d').strftime('%A')),
                                            categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                            ordered=True)
data_by_day['weekend'] = np.where(data_by_day['day_of_week'].isin(['Saturday', 'Sunday']), 'Weekend', 'Weekday')

# Function to produce summary statistics (mean and +/- sd)
def data_summary(x):
    m = np.mean(x)
    ymin = m - np.std(x)
    ymax = m + np.std(x)
    return m, ymin, ymax

# Plot the number of steps per day type
plt.figure(figsize=(10, 7.5))
sns.violinplot(x='day_of_week', y='stepsPerDay', data=data_by_day, inner=None, alpha=0.5)
sns.pointplot(x='day_of_week', y='stepsPerDay', data=data_by_day, estimator=np.mean, ci='sd', color='black')
plt.xlabel("")
plt.ylabel("Steps per day")
# plt.savefig("Plots/stepsPerDay.png", dpi=300)
plt.show()
plt.close()