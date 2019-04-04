import os
import csv
import requests
import json
from collections import OrderedDict

print("Hi Parker. Welcome to my submission. We will be getting weather data based on the information you provide (or choose not to provide).")

# get whether user would like to set a location
user_set_location = input(
    "Would you like to set a location? 'y' for yes, 'n' for no: ")

# use boolean for easier processing later on
user_set_location = (user_set_location in ['y', 'Y', 'yes', 'Yes'])

# get location from user if user wanted to set a location
if user_set_location:
    location = input("Location: ")
else:
    print("You have chosen not to set a location. Default location is San Francisco. This location will be used.")

# get whether user would like to set a date
user_set_date = input(
    "Would you like to set a date? 'y' for yes, 'n' for no: ")

# ''
user_set_date = (user_set_date in ['y', 'Y', 'yes', 'Yes'])

# get date from user if user wanted to set a date
if user_set_date:
    year = input("Year: ")
    month = input("Month: ")
    day = input("Day: ")
else:
    print("You have chosen not to set a date. You will get the weather for today and the next 5 days as a csv. Raw data is saved to a json file.")


if user_set_location:
    # create location url using input location from user
    location_id_url = 'https://www.metaweather.com/api/location/search/?query=%s' % (
        location)

    # get woeid of location
    location_id = json.loads(requests.get(location_id_url).text)[0]['woeid']

if user_set_location and not user_set_date:

    # create weather url using woeid, no input date
    weather_url = 'https://www.metaweather.com/api/location/%s/' % (
        location_id)

elif user_set_location and user_set_date:

    # create weather url using woeid and input date
    weather_url = 'https://www.metaweather.com/api/location/%s/%s/%s/%s' % (
        location_id, year, month, day)

elif not user_set_location and user_set_date:

    # create weather_url using input date, use San Francisco default location
    weather_url = 'https://www.metaweather.com/api/location/2487956/%s/%s/%s' % (
        year, month, day)

elif not user_set_location and not user_set_date:

    # create weather url using San Francisco default location, no input date
    weather_url = 'https://www.metaweather.com/api/location/2487956/'

# get weather data
weather_data = json.loads(requests.get(weather_url).text)

# append raw data to raw_weather_data.json exists, write if
# raw_weather_data.json does not exist
if os.path.isfile('raw_weather_data.json'):
    file_setting = 'a'
else:
    file_setting = 'w'

# save/append raw data to file
with open('raw_weather_data.json', file_setting) as outfile:
    outfile.write('%s\n' % (json.dumps(weather_data)))

if not user_set_date:
    # make weather_data dict into OrderedDict to put 'created' first
    ordered_weather_data = [OrderedDict(item) for item in weather_data[
        'consolidated_weather']]

else:
    # ''
    ordered_weather_data = [OrderedDict(item) for item in weather_data]

# put 'created' first for all items in ordered_weather_data
for item in ordered_weather_data:
    item.move_to_end('created', last=False)


# get fieldnames which will be used in csv header cells
fieldnames = ordered_weather_data[0].keys()

# create csvfile
with open("weather.csv", "w") as csvfile:

    # initialize DictWriter from csv module
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # write header based on fieldnames in DictWriter initialization
    writer.writeheader()

    # write row for each item in ordered_weather_data
    for item in ordered_weather_data:
        writer.writerow(item)
