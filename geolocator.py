#!/usr/bin/env python
# thom o'connor
# begin: 2017-01-21
# uses https://developers.google.com/maps/documentation/geocoding
# purpose: parse CSV input file, extract street addresses, query 
#    Google Maps Geocoding API to retrieve geolocation data as "lat, lon"
# note: you will need an API key from:
#    https://developers.google.com/maps/documentation/geocoding/get-api-key
# run:
#    ./geolocator.py -f file.csv

import sys
import argparse
import googlemaps
import csv
from pprint import pprint
import re
import simplejson as json

# optional debugger
#import pdb
#db.set_trace()

# config
mydebug = 0  # debug flag, set to taste
# Googlemaps client key (required)
gmaps = googlemaps.Client(key='[MY-GOOGLE-API-KEY]')
# output file with lat/lon data as "lat,lon"
outputfile = "latlon-output.txt"

# process args
parser = argparse.ArgumentParser(description='Process filename')
parser.add_argument('-f', nargs='*', help='input filename')
parser.add_argument('myfilename', nargs='+', help='filename of CSV data with "Address,City,State,ZIP,Country" in CSV fields 1 to 5')
args = parser.parse_args()

# file output
f = open(outputfile, 'a')

if mydebug > 1:
    print("DEBUG: myfilename=" + args.myfilename[0])

def geocode_address(mygmaps, myloc):
    if mydebug > 2:
        print("DEBUG: mygmaps=" + str(mygmaps))
        print("DEBUG: myloc=" + str(myloc))
    try:
        geocode_result = mygmaps.geocode(myloc)
    except:
        print("ERROR: ", sys.exc_info()[0])
        return(None)
    if mydebug > 2:
        pprint("DEBUG: ")
        pprint(geocode_result)
    return(geocode_result)

def as_complex(dct):
    if '__complex__' in dct:
        return complex(dct['real'], dct['imag'])
    return dct

def json_parse(json_string):
    if mydebug > 2:
        print("DEBUG: start json_parse={0}".format(json_string))
    try:
        parsed_json = json.loads(json_string,object_hook=as_complex)
    except:
        print("ERROR: ", sys.exc_info()[0])
        return(False)
    if mydebug > 2:
        pprint(parsed_json)
    return(parsed_json)

def get_latlon(mygeocode_entry):
    if mydebug > 2:
        print("DEBUG: start get_latlon={0}".format(mygeocode_entry))
    # localize vars
    lat = None
    lon = None
    # check for existence of fields
    if mygeocode_entry["geometry"]["location"]["lat"] and mygeocode_entry["geometry"]["location"]["lng"]:
        lat = mygeocode_entry["geometry"]["location"]["lat"]
        lon = mygeocode_entry["geometry"]["location"]["lng"]
    if mydebug > 2:
         print("DEBUG: lat={0}, lon={1}".format(lat, lon))
    return(lat,lon)

# main()
with open(args.myfilename[0], 'rt', encoding='utf-8', errors='ignore') as csvfile:
    # use csv.reader to parse file fields
    myreader = csv.reader(csvfile, delimiter=',', quotechar='"')

    # loop through input file
    for row in myreader:
        if mydebug > 2:
            print("DEBUG: loop start")
        if mydebug > 0:
            print(', '.join(row))
            # print("row=" + join(row))
        # exclude comment lines in input file
        if re.match('^#',row[0]):
            continue
        # address is fields 1-5 of my input file (your mileage may vary)
        # address, city, state, zip, country
        myfulladdress = ", ".join(row[1:6])
        if mydebug > 0:
            print("DEBUG: myfulladdress=" + str(myfulladdress))
        # get geocode results for myfulladdress
        geocode_result = geocode_address(gmaps,myfulladdress)
        if geocode_result is not None:
            # geocode_result is a list not a dict
            for entry in range(len(geocode_result)):
                if mydebug > 2:
                    print("DEBUG: entry {0} = {1}".format(entry,geocode_result[entry]))
                mylat,mylon = get_latlon(geocode_result[entry])
                if (mylat is not None) and (mylon is not None):
                    f.write(str(mylat) + "," + str(mylon) + "\n")
        if mydebug > 2:
            print("DEBUG: loop end")

f.close()
exit()
