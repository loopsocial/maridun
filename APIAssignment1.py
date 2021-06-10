import csv
import json

import requests

import a1constants


# helper function to write to csv from list, all lines at once
def write_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)  # write all rows at once


# helper function to get json from spacex API
def call_api(path, params):
    if path in a1constants.endpoints.keys():
        path = a1constants.endpoints[path]
    url = f'{a1constants.BASE_SPACEX_URL}{path}'
    res = requests.get(url, params=params)
    json_res = json.loads(res.content)  # JSON -> dictionary
    return json_res


# 1. Write a function that would provide the below mentioned rocket and payload details
# for the latest historical event.
# Rocket name
# Rocket height and diameter in meters
# Payload id
# Payload nationality and mass in kg
def extract_rocket_details():
    # list stores attributes for output, will write to csv later
    info = [["Rocket_Name", "Rocket_Height", "Rocket_Diameter", "Payload_id",
             "Payload_nationality", "Payload_mass"]]  # set headers
    params = {
        'sort': 'event_date_utc',
        'order': 'desc'  # ordering by event date desc to get the latest historical event at index 0
    }
    json_res = call_api('history', params)
    most_recent_event = json_res[0]
    flight_num = most_recent_event['flight_number']  # extracts flight number from event

    # use flight_num to get info from launches page
    params = {'flight_number': flight_num}
    json_res = call_api('launches', params)
    rocket_info = json_res[0]['rocket']
    rocket_id = rocket_info['rocket_id']

    # use rocket_id to get dimensions from rockets page
    params = {}
    json_res = call_api(f'rockets/{rocket_id}', params)
    # extract relevant attributes re. rocket
    rocket_name = json_res['rocket_name']
    rocket_height = json_res['height']['meters']
    rocket_diameter = json_res['diameter']['meters']

    for payload in rocket_info['second_stage']['payloads']:
        # use a loop since payloads is a list, each flight could have >1 payload
        # extract relevant attributes re. payload
        payload_id = payload['payload_id']
        payload_nationality = payload['nationality']
        payload_mass = payload['payload_mass_kg']
        # one row in the csv for each payload, rocket can be duplicated
        info.append([rocket_name, rocket_height, rocket_diameter, payload_id, payload_nationality, payload_mass])

    write_csv(info, 'rocketdetails.csv')


# 2. Write a function that would take flight number as input and output
# a text file with details about all ships that assisted for that flight
# and also other missions these ships have ever assisted. The text file should contain three columns:
# Ship Name
# Mission Name
# Flight Name
def extract_ship_details(flight_number):
    # list stores attributes for output, will write to csv later
    rows = [["Ship_Name", "Mission_Name", "Flight_number"]]  # add headers
    params = {'flight_number': flight_number}
    json_res = call_api('launches', params)
    ships = json_res[0]['ships']  # getting info on participating ships
    for ship in ships:
        params = {'ship_id': ship}
        json_res = call_api('ships', params)
        missions = json_res[0]['missions']  # get all missions for each ship
        for mission in missions:
            mission_name = mission['name']
            flight_no = mission['flight']
            # print([ship, mission_name, flight_no])
            rows.append([ship, mission_name, flight_no])  # will be added to csv

    write_csv(rows, 'shipdetails.csv')


if __name__ == "__main__":
    extract_rocket_details()
    extract_ship_details(20)
