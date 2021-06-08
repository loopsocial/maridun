import json
import requests
import csv

# 1. Write a function that would provide the below mentioned rocket and payload details
# for the latest historical event.
# Rocket name
# Rocket height and diameter in meters
# Payload id
# Payload nationality and mass in kg
def rocketdetails():
    info = [] #stores attributes for output, will write to csv later
    #set headers
    info.append(["Rocket_Name", "Rocket_Height", "Rocket_Diameter", "Payload_id", "Payload_nationality", "Payload_mass"])
    params = {
        'sort': 'event_date_utc',
        'order': 'desc' #ordering by event date desc to get the latest historical event at index 0
    }
    url = 'https://api.spacexdata.com/v3/history'
    res = requests.get(url, params=params)
    json_res = json.loads(res.content)  # JSON -> dictionary
    mostRecentEvent = json_res[0]
    #print(mostRecentEvent)
    flightnum = mostRecentEvent['flight_number'] #extracts flight number from event

    #use flightnum to get info from launches page
    params = {
        'flight_number': flightnum
    }
    url = 'https://api.spacexdata.com/v3/launches'
    res = requests.get(url, params=params)
    json_res = json.loads(res.content)  # JSON -> dictionary
    rocket_info = json_res[0]['rocket']
    rocket_id = rocket_info['rocket_id']

    # # use rocket_id to get dimensions from rockets page
    url = f'https://api.spacexdata.com/v3/rockets/{rocket_id}'
    res = requests.get(url)
    json_res = json.loads(res.content)  # JSON -> dictionary

    #extract relevant attributes re. rocket
    #print(json_res['rocket_name'])
    rocket_name = json_res['rocket_name']
    #print(json_res['height']['meters'])
    rocket_height = json_res['height']['meters']
    #print(json_res['diameter']['meters'])
    rocket_diameter = json_res['diameter']['meters']

    for payload in rocket_info['second_stage']['payloads']:
        #use a loop since payloads is a list, each flight could have >1 payload
        #extract relevant attributes re. payload
        payload_id = payload['payload_id']
        payload_nationality = payload['nationality']
        payload_mass = payload['payload_mass_kg']
        #one row in the csv for each payload, rocket can be duplicated
        info.append([rocket_name, rocket_height, rocket_diameter, payload_id, payload_nationality, payload_mass])



    with open('rocketdetails.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(info)

# 2. Write a function that would take flight number as input and output
# a text file with details about all ships that assisted for that flight
# and also other missions these ships have ever assisted. The text file should contain three columns:
# Ship Name
# Mission Name
# Flight Name
def shipdetails(flightnumber):
    rows = [] #stores attributes for output, will write to csv later
    rows.append(["Ship_Name", "Mission_Name", "Flight_number"]) #headers
    params = {
        'flight_number': flightnumber
    }
    url = 'https://api.spacexdata.com/v3/launches'
    res = requests.get(url, params=params)
    json_res = json.loads(res.content)
    ships = json_res[0]['ships'] #getting info on participating ships
    for ship in ships:
        params = {
            'ship_id': ship
        }
        url = 'https://api.spacexdata.com/v3/ships'
        res = requests.get(url, params=params)
        json_res = json.loads(res.content)  # JSON -> dictionary
        missions = json_res[0]['missions'] #get all missions for each ship
        for mission in missions:
            mname = mission['name']
            flightno = mission['flight']
            #print([ship, mname, flightno])
            rows.append([ship, mname, flightno]) #will be added to csv

    with open('shipdetails.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows) #write all rows at once


if __name__== "__main__":
    rocketdetails()
    shipdetails(20)