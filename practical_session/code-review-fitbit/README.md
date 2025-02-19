# Code review of `exploreStepsData` script


## Message to reviewer:

> Hi, please can you review exploreStepsData.R (or exploreStepsData.py). I got as far as loading my downloaded fitbit data into R/Python and creating some initial exploratory plots. The plots include looking at the time interval between step data collection and how many steps I do per day. If you want to see these plots they're at my repo here: https://github.com/AmeliaES/fitbitr 

> A quick walk through of the code and what it does: 

* Load in libraries, create colour schemes, set the ggplot theme.
* Load in the data (which is in json format) and extract the date/time stamp and number of steps
* Calculate the intervals between times when step data is recorded.
* Plot time between data collection and number of steps, to see if there's any relationship.
* Have a look at how many steps i do per hour (for each day)
* Then split that into weekdays and weekends and explore the mean steps on each day type (I managed to make a function to help with that one!)

> Many thanks for your time, any feedback or suggested changes would be much appreciated.





