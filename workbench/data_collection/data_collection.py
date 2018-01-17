import json, urllib, csv
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))
from csv_to_json import convert_csv_to_json
from align_strings import align_strings
from sodapy import Socrata


score_thresh = 0.8 # for name comparisons/alignments
unique_food_headers = ['results, inspection_id', 'license_', 'violations', 'risk', 'inspection_type', 'inspection_date']
repeated_food_headers = [':@computed_region_bdys_3d7i', ':@computed_region_43wa_7qmu', ':@computed_region_6mkv_f3dw', ':@computed_region_awaf_s7ux', ':@computed_region_vrxf_vc4k', 'dba_name', 'city', 'zip', 'facility_type', 'state', 'location', 'latitude', 'aka_name', 'address', 'longitude']
unique_osha_headers = ['Part of Body', 'Source', 'Final Narrative', 'Nature', 'Hospitalized', 'Primary NAICS', 'Amputation', 'Secondary Source', 'Part of Body Title', 'Secondary Source Title', 'Inspection', 'ID', 'EventTitle', 'SourceTitle', 'EventDate', 'NatureTitle', 'Event', 'UPA']
repeated_osha_headers = ['City', 'Zip', 'Employer', 'State', 'Latitude', 'Longitude', 'Address1', 'Address2']

osha = open("severeinjury.csv", 'r')
osha_text = unicode(osha.read(), errors = 'ignore')
osha2 = open("severeinjury.csv", 'w')
osha2.write(osha_text)
osha2.close()

business_license_client = Socrata("data.cityofchicago.org", '9HlT94OOuLOGZeRGk9okbPYA2')
business_license_data = business_license_client.get("xqx5-8hwx", limit=2000)

convert_csv_to_json("severeinjury.csv", "severeinjury.json", "Employer")

def load_file(file_name):
    file = open(file_name, 'r')
    return json.loads(file.read())

food_inspection_data = load_file("cityofchicagofood.json")
osha_injury_data = load_file("severeinjury.json")

def combine_data_by_dbaname(unique_headers, repeated_headers, dba_header, lat_header, lon_header, database):
    combined_data = {}
    if type(database) is dict:
        database = database.values()
        newdatabase = []
        for case in database:
            if (case['City'] == "CHICAGO"):
                newdatabase.append(case)
        database = newdatabase
    for case1 in database:
        for case2 in database:
            if cmp(case1,case2) != 0:
                if dba_header in case1 and dba_header in case2:
                    c1_name = case1[dba_header]
                    c2_name = case2[dba_header]
                    if c1_name not in combined_data:
                        combined_data[c1_name] = {}
                        for repeat_header in repeated_headers:
                            if repeat_header in case1:
                                combined_data[c1_name].update({repeat_header: case1[repeat_header]})
                        for unique_header in unique_headers:
                            if unique_header in case1:
                                combined_data[c1_name].update({unique_header: [case1[unique_header]]})
                            else:
                                combined_data[c1_name][unique_header] = []
                    lats_included = lat_header in case1 and lat_header in case2
                    lons_included = lon_header in case1 and lon_header in case2
                    if lats_included and lons_included:
                        lats_match = case1[lat_header] == case2[lat_header]
                        lons_match = case2[lon_header] == case1[lon_header]
                        if lats_match and lons_match:
                                align_score = align_strings(c1_name, c2_name)[0]
                                if align_score > score_thresh:
                                    for unique_header in unique_headers:
                                        if unique_header in case2:
                                            combined_data[c1_name][unique_header].append(case2[unique_header])
    return combined_data

def count_frequency(db1, db1_name, db1_dbaheader, db1_unique_header, db2, db2_name, db2_dbaheader, db2_unique_header):
    frequency_data = {}
    for case1 in db1:
        frequency_data[case1] = {}
        frequency_data[case1][db1_name] = db1[case1]
        frequency_data[case1]["Frequency"] = len(frequency_data[case1][db1_name][db1_unique_header])
        for case2 in db2:
            align_score = align_strings(case1, case2)[0]
            if align_score > score_thresh:
                frequency_data[case1]["Frequency"] += len(frequency_data[case2][db2_name][db2_unique_header])
                frequency_data[case1][db2_name] = db2[case2]
                print case1, case2
            else:
                frequency_data[case2] = {}
                frequency_data[case2][db2_name] = db2[case2]
                frequency_data[case2]["Frequency"] = len(frequency_data[case2][db2_name][db2_unique_header])
    return frequency_data


food_json = combine_data_by_dbaname(unique_food_headers, repeated_food_headers, 'dba_name', 'latitude', 'longitude', food_inspection_data)
osha_json = combine_data_by_dbaname(unique_osha_headers, repeated_osha_headers, 'Employer', 'Latitude', 'Longitude', osha_injury_data)

combined_databases = count_frequency(food_json, "food_inspection", 'dba_name', 'inspection_date', osha_json, "OSHA", 'Employer', 'ID')

output_file = open("output.txt", 'w')
output_file.write(json.dumps(combined_databases))
