import json, urllib, csv
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))
from csv_to_json import convert_csv_to_json
from align_strings import align_strings
from sodapy import Socrata


score_thresh = 0.75 # for name comparisons/alignments
unique_food_headers = ['hourvoice_id','results, inspection_id', 'license_', 'violations', 'risk', 'inspection_type', 'inspection_date']
repeated_food_headers = [':@computed_region_bdys_3d7i', ':@computed_region_43wa_7qmu', ':@computed_region_6mkv_f3dw', ':@computed_region_awaf_s7ux', ':@computed_region_vrxf_vc4k', 'dba_name', 'city', 'zip', 'facility_type', 'state', 'location', 'latitude', 'aka_name', 'address', 'longitude']
unique_osha_headers = ['hourvoice_id','Part of Body', 'Source', 'Final Narrative', 'Nature', 'Hospitalized', 'Primary NAICS', 'Amputation', 'Secondary Source', 'Part of Body Title', 'Secondary Source Title', 'Inspection', 'ID', 'EventTitle', 'SourceTitle', 'EventDate', 'NatureTitle', 'Event', 'UPA']
repeated_osha_headers = ['City', 'Zip', 'Employer', 'State', 'Latitude', 'Longitude', 'Address1', 'Address2']
unique_business_headers = ['id', 'license_id', 'site_number', 'license_code', 'license_description', 'business_activity_id', 'business_activity', 'license_number', 'application_type', 'application_created_date', 'application_requirements_complete', 'payment_date', 'conditional_approval', 'license_term_start_date', 'license_term_expiration_date', 'license_approved_for_issuance', 'date_issued', 'license_status', 'license_status_change_date']
repeated_business_headers = ['account_number', 'legal_name', 'doing_business_as_name', 'address', 'city', 'state', 'zip_code', 'ward', 'precinct', 'ward precinct', 'police_district', 'ssa', 'latitude', 'longitude', 'location']

osha = open("severeinjury.csv", 'r')
osha_text = unicode(osha.read(), errors = 'ignore')
osha.close()
osha2 = open("severeinjury.csv", 'w')
osha2.write(osha_text)
osha2.close()

business_license_client = Socrata("data.cityofchicago.org", '9HlT94OOuLOGZeRGk9okbPYA2')
business_license_data = business_license_client.get("xqx5-8hwx", limit=1000)
convert_csv_to_json("severeinjury.csv", "severeinjury.json", "Employer")

def load_file(file_name):
    f = open(file_name, 'r')
    return json.loads(f.read())

food_inspection_data = business_license_client.get("cwig-ma7x", limit=1000)
osha_injury_data = load_file("severeinjury.json")

id_counter = 0
for case in food_inspection_data:
    case["hourvoice_id"] = id_counter
    id_counter+=1

for case in osha_injury_data:
    osha_injury_data[case]["hourvoice_id"] = id_counter
    id_counter+=1

for case in business_license_data:
    case["hourvoice_id"] = id_counter
    id_counter+=1

def combine_data_by_dbaname(unique_headers, repeated_headers, dba_header, lat_header, lon_header, database):
    combined_data = {}
    if type(database) is dict:
        database = database.values()
        newdatabase = []
        for case in database:
            if (case['City'] == "CHICAGO"):
                newdatabase.append(case)
        database = newdatabase
    visited = set()
    for case1 in database:
        if case1['hourvoice_id'] in visited:    # already been added
            continue
        for case2 in database:
            if case2['hourvoice_id'] in visited:    # already been added
                continue
            if cmp(case1,case2) != 0:
                if dba_header in case1 and dba_header in case2:
                    c1_name = case1[dba_header]
                    c2_name = case2[dba_header]
                    c1_hv_id = case1["hourvoice_id"]
                    c2_hv_id = case2["hourvoice_id"]
                    if c1_hv_id not in combined_data:
                        combined_data[c1_hv_id] = {"hourvoice_id": c1_hv_id}
                        for repeat_header in repeated_headers:
                            if repeat_header in case1:
                                combined_data[c1_hv_id].update({repeat_header: case1[repeat_header]})
                        for unique_header in unique_headers:
                            if unique_header in case1:
                                combined_data[c1_hv_id].update({unique_header: [case1[unique_header]]})
                            else:
                                combined_data[c1_hv_id][unique_header] = []
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
                                        combined_data[c1_hv_id][unique_header].append(case2[unique_header])
                                visited.add(case2['hourvoice_id'])
        visited.add(case1['hourvoice_id'])
    return combined_data

def count_frequency(db1, db1_name, db1_dbaheader, db1_unique_header, db2, db2_name, db2_dbaheader, db2_unique_header):
    frequency_data = {}
    visited = set()
    for case1 in db1:
        if case1 in visited:    # already been added
            continue
        frequency_data[case1] = {}
        frequency_data[case1][db1_name] = db1[case1]
        frequency_data[case1]["Frequency"] = len(frequency_data[case1][db1_name][db1_unique_header])
        for case2 in db2:
            if case2 in visited:    # already been added
                continue
            align_score = align_strings(db1[case1][db1_dbaheader], db2[case2][db2_dbaheader])[0]
            if align_score > score_thresh:
                frequency_data[case1]["Frequency"] += len(db2[case2][db2_unique_header])
                frequency_data[case1][db2_name] = db2[case2]
                visited.add(case2)
                if case2 in frequency_data:
                    del frequency_data[case2]
            elif case2 not in visited:
                frequency_data[case2] = {}
                frequency_data[case2][db2_name] = db2[case2]
                frequency_data[case2]["Frequency"] = len(frequency_data[case2][db2_name][db2_unique_header])
        visited.add(case1)
    return frequency_data


food_json = combine_data_by_dbaname(unique_food_headers, repeated_food_headers, 'dba_name', 'latitude', 'longitude', food_inspection_data)
osha_json = combine_data_by_dbaname(unique_osha_headers, repeated_osha_headers, 'Employer', 'Latitude', 'Longitude', osha_injury_data)
print "length before: " + str(len(food_json)) + str(len(osha_json))

business_json = combine_data_by_dbaname(unique_business_headers, repeated_business_headers, 'doing_business_as_name', 'latitude', 'longitude', business_license_data)
sub_combined_databases = count_frequency(food_json, "food_inspection", 'dba_name', 'inspection_date', osha_json, "OSHA", 'Employer', 'ID')
print "length after: " + str(len(sub_combined_databases))

combined_databases = {}
for case1 in business_json:
    combined_databases[case1] = business_json[case1]
    for case2 in sub_combined_databases:
        align_score = 0
        latitudes_match = False
        longitudes_match = True
        if 'food_inspection' in sub_combined_databases[case2]:
            align_score = align_strings(business_json[case1]['doing_business_as_name'], sub_combined_databases[case2]['food_inspection']['dba_name'])[0]
            if 'latitude' in sub_combined_databases[case2]['food_inspection'] and 'latitude' in business_json[case1]:
                latitudes_match = round(sub_combined_databases[case2]["food_inspection"]["latitude"], 6) == round(business_json[case1]["latitude"], 6)
            if 'longitude' in sub_combined_databases[case2]['food_inspection'] and 'longitude' in business_json[case1]:
                longitudes_match = round(sub_combined_databases[case2]["food_inspection"]["longitude"], 6) == round(business_json[case1]["longitude"], 6)
        if 'OSHA' in sub_combined_databases[case2]:
            align_score = align_strings(business_json[case1]['doing_business_as_name'], sub_combined_databases[case2]['OSHA']['Employer'])[0]
            if 'Latitude' in sub_combined_databases[case2]['OSHA'] and 'latitude' in business_json[case1]:
                latitudes_match = sub_combined_databases[case2]["OSHA"]["Latitude"] == round(business_json[case1]["latitude"], 2)
            if 'Longitude' in sub_combined_databases[case2]['OSHA'] and 'longitude' in business_json[case1]:
                longitudes_match = sub_combined_databases[case2]["OSHA"]["Longitude"] == round(business_json[case1]["longitude"], 2)
        if align_score > score_thresh and (latitudes_match and longitudes_match):
            combined_databases[case1]["violations"] = sub_combined_databases[case2]

output_file = open("output.txt", 'w')
output_file.write(json.dumps(combined_databases))
