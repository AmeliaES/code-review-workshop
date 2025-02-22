# Analyse steps data from my FitBit
# Ideas:
# Find out how many steps I do a day on average
# Find out if there's a relationship with time of year, eg. less active in winter more active in summer
# Find out if there's a relationship with the day, eg. weekday or weekend
# Find out when during the day am I usually most active

# Explore missing data, could my results be bias because I don't wear my fitbit at certain times in the day?
# Also need to find out what sets the intervals in data collection when I am wearing my fitbit, as i dont think it's every minute...

# ------------------------------
# Load libraries
library(rjson) # for reading in JSON files - steps data from fitbit is json
library(stringr)
library(dplyr)
library(lubridate) # for manipulating dates and times
library(hms) # for manipulating times
library(tibble)
library(ggplot2)
library(scales) # allows labeling of axes in ggplot to change scientific notation to using commas for big numebrs
library(tidyr)
# ------------------------------
# Set ggplot theme
# Define season colours
seasonColours <- c("Spring" = "#a0c73e",
                   "Summer" = "#e35bd2",
                   "Autumn" = "#f5ae2c",
                   "Winter" = "#afd3e3")

# Define colours for the night
nightColours <- c("night" = "#6f6278",
                  "dawnDusk" = "#d9b6b8",
                  "day" = "#f9fade")

# Custom theme with defined colors
custom_theme <- function() {
  theme_minimal() +
    theme(text = element_text(size = 15))
}

# Set the custom theme globally
theme_set(custom_theme())


# ------------------------------
# Load data
# Find all files that contain raw steps data (lots of the files are in JSON format)
pathSteps <- "/Users/aes/GitRepos/fitbitr/Takeout/Fitbit/Global Export Data/"
dates <- list.files(pathSteps) %>%
  str_subset("steps") %>% # only files containing steps
  str_extract("\\d{4}-\\d{2}-\\d{2}") %>% # extract just the date part
  str_subset("^2017", negate = T) # remove dates in 2017, as this was data from a different fitbit

# Loop over each date to extract the steps data from each file
data <- lapply(dates, function(date){
steps <- fromJSON(file= paste0(pathSteps, "steps-",date,".json"))

data <- data.frame( dateTime = unname(unlist(sapply(steps,function(x) x[1]))) , # extracts the date and time stamp
                    steps = as.numeric(unname(unlist(sapply(steps,function(x) x[2]))))) # extracts the number of steps

return(data)
}) %>% do.call(rbind,.)


# ------------------------------
# Extract date from the dateTime stamp. Date is in the format of MM/DD/YY, time is HH:MM:SS
data <- data %>%
  mutate(dateTime = as_datetime(dateTime, format = "%m/%d/%y %H:%M:%S")) %>%
  mutate(date = date(dateTime)) %>%
  mutate(time = as_hms(dateTime)) %>%
  as.tibble()

# ------------------------------
# Whats the interval between times?
data <- data %>%
  group_by(date) %>% # this ensures intervals are only done per day
  arrange(date, time) %>%
  mutate(interval = as.numeric(difftime(lead(dateTime), dateTime, units = "mins"))) %>%
  ungroup()

# check
data %>%
  filter(date == "2022-07-06" | date == "2022-07-07") %>%
  print(n = nrow(.))
# at the end of 6th the entry for interval is NA, which is what we expect.

# Plot the interval per steps
png("Plots/intervals.png", res = 300, height = 1500, width = 3000)
print(
data %>%
  drop_na() %>%
ggplot(data = .) +
  geom_point(aes(x = interval/60, y = steps), alpha = 0.5) +
  labs(x = "Time between data collection (hours)",
       y = "Number of steps")
)
dev.off()
# Hard to see a relationship here, also interval may be high when i take the fitbit off for times during the day
# but even when I am wearing it it looks like it's not collecting data every minute
# why is there a minus point?

# ------------------------------
# Add up the amount of steps per hour per date
dataByHour <- data %>%
  group_by(date, hour = hour(dateTime)) %>%
  summarise(total_steps = sum(steps)) %>%
  ungroup()

head(dataByHour)

min(dataByHour$hour)
# this is 0, change to 1, as it's more intuitive for hour to be 1 to 24 not 0 to 23
dataByHour <- dataByHour %>%
  mutate(hour = hour + 1)

# Check that is correct
data %>%
  filter(date == "2022-07-06") %>%
  filter(hour(time) == 16) %>%
  pull(steps) %>% sum() # looks good, same as in dataByHour

# ------------------------------
# Data of steps per day
dataByDay <- dataByHour %>%
  group_by(date) %>%
  summarise(stepsPerDay = sum(total_steps))

# ------------------------------
# Split into weekday/weekend
dataByHour <- dataByHour %>%
  mutate(day_of_week = factor(weekdays(date), levels = c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))) %>%
  mutate(weekend = ifelse(day_of_week %in% c("Saturday", "Sunday"), "Weekend", "Weekday"))

dataByDay <- dataByDay %>%
  mutate(day_of_week = factor(weekdays(date), levels = c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))) %>%
  mutate(weekend = ifelse(day_of_week %in% c("Saturday", "Sunday"), "Weekend", "Weekday"))

# Function to produce summary statistics (mean and +/- sd)
data_summary <- function(x) {
  m <- mean(x)
  ymin <- m-sd(x)
  ymax <- m+sd(x)
  return(c(y=m,ymin=ymin,ymax=ymax))
}

# Plot the number of steps per day type
png("Plots/stepsPerDay.png", res = 300, height = 1500, width = 2000)
print(
dataByDay %>%
ggplot(data = ., aes( x = day_of_week, y = stepsPerDay)) +
  geom_violin(fill = "deepskyblue4", alpha = 0.5)+
  stat_summary(fun.data=data_summary) +
  labs(x = "",
       y = "Steps per day") +
  scale_y_continuous(labels = label_number(big.mark = ",", decimal.mark = ".", suffix = ""))
)
dev.off()
