import os
import sys
import csv
import requests
import json
import argparse
from collections import OrderedDict
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--location', nargs=1)
parser.add_argument('--date', nargs=1)

args = parser.parse_args()

# did user set location?
user_set_location = (args.location != None)

# did user set date?
user_set_date = (args.date != None)

if user_set_date:

    datetime_object = datetime.strptime(args.date[0], '%m/%d/%Y')

    # set year, month, day
    year = datetime_object.year
    month = datetime_object.month
    day = datetime_object.day


if user_set_location:
    # create location url using input location from user
    location_id_url = 'https://www.metaweather.com/api/location/search/?query=%s' % (
        args.location[0])

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
