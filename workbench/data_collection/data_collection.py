import json, urllib, csv
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))
from csv_to_json import convert_csv_to_json
from align_strings import align_strings
from sodapy import Socrata


score_thresh = 0.8 # for name comparisons/alignments

# Headers marked 'unique' are headers under which information that is unique to
# datapoint in consideration are stored. Headers marked 'repeat' contain
# information which are repeated across datapoints of the same business & location
# (i.e. latitude and longitude are categorized as repeat headers because
# if one business at a specific location has multiple violations, the latitude
# and longitude of the business won't change, while inspection_date is a unique header
# because each inspection should be on a different day/at a different time,
# even if it is an inspection of the same business)
unique_food_headers       = ['hourvoice_id','results, inspection_id', 'license_',
                             'violations', 'risk', 'inspection_type', 'inspection_date']
repeated_food_headers     = [':@computed_region_bdys_3d7i', ':@computed_region_43wa_7qmu',
                             ':@computed_region_6mkv_f3dw', ':@computed_region_awaf_s7ux',
                             ':@computed_region_vrxf_vc4k', 'dba_name', 'city', 'zip',
                             'facility_type', 'state', 'location', 'latitude', 'aka_name',
                             'address', 'longitude']
unique_osha_headers       = ['hourvoice_id','Part of Body', 'Source', 'Final Narrative',
                             'Nature', 'Hospitalized', 'Primary NAICS', 'Amputation',
                             'Secondary Source', 'Part of Body Title',
                             'Secondary Source Title', 'Inspection', 'ID',
                             'EventTitle', 'SourceTitle', 'EventDate', 'NatureTitle',
                             'Event', 'UPA']
repeated_osha_headers     = ['City', 'Zip', 'Employer', 'State', 'Latitude',
                             'Longitude', 'Address1', 'Address2']
unique_business_headers   = ['hourvoice_id', 'id', 'license_id', 'site_number', 'license_code',
                             'license_description', 'business_activity_id',
                             'business_activity', 'license_number', 'application_type',
                             'application_created_date', 'application_requirements_complete',
                             'payment_date', 'conditional_approval',
                             'license_term_start_date', 'license_term_expiration_date',
                             'license_approved_for_issuance', 'date_issued',
                             'license_status', 'license_status_change_date']
repeated_business_headers = ['account_number', 'legal_name', 'doing_business_as_name',
                             'address', 'city', 'state', 'zip_code', 'ward',
                             'precinct', 'ward precinct', 'police_district',
                             'ssa', 'latitude', 'longitude', 'location']

# fixing unicode error in order to convert severeinjury.csv to a json
osha = open("severeinjury.csv", 'r')
osha_text = unicode(osha.read(), errors = 'ignore')
osha.close()
osha2 = open("severeinjury.csv", 'w')
osha2.write(osha_text)
osha2.close()

# accessing food inspection and business license APIs from city of chicago databases
business_license_client = Socrata("data.cityofchicago.org", '9HlT94OOuLOGZeRGk9okbPYA2')
business_license_data = business_license_client.get("xqx5-8hwx", limit=1000)
food_inspection_data = business_license_client.get("cwig-ma7x", limit=1000)

# converts OSHA database to json and reads data
convert_csv_to_json("severeinjury.csv", "severeinjury.json", "Employer")
osha_file = open("severeinjury.json", 'r')
osha_injury_data = json.loads(osha_file.read())

# adds unique id to each datapoint in each database
# ids do not repeat across databases
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

# used in consolidate_data_by_dbaname to verify that two companies are the same
def compare_lats_lons_and_dbaname(case1, case2, lat_header, lon_header, c1_name, c2_name):
    lats_included = lat_header in case1 and lat_header in case2
    lons_included = lon_header in case1 and lon_header in case2
    if lats_included and lons_included:
        lats_match = case1[lat_header] == case2[lat_header]
        lons_match = case2[lon_header] == case1[lon_header]
        if lats_match and lons_match:
            align_score = align_strings(c1_name, c2_name)[0]
            return align_score > score_thresh

# used in consolidate_data_by_dbaname to add a new case to the final database
def create_new_entry(database, hv_id, case, repeated_headers, unique_headers):
    database[hv_id] = {"hourvoice_id": hv_id}
    for repeat_header in repeated_headers:
        if repeat_header in case:
            database[hv_id].update({repeat_header: case[repeat_header]})
    for unique_header in unique_headers:
        if unique_header in case:
            database[hv_id].update({unique_header: [case[unique_header]]})
        else:
            database[hv_id][unique_header] = []

# consolidates databases so that businesses with more than one violation are represented
# by only one data point, while still containing all of the necessary violation-specific
# information. The hourvoice_id becomes the representative element of the datapoint
def consolidate_data_by_hv_id(unique_headers, repeated_headers, dba_header, lat_header, lon_header, database):
    consolidated_data = {}
    visited = set()

    if type(database) is dict:
        database = database.values()
        newdatabase = []
        for case in database:
            if (case['City'] == "CHICAGO"):   # singling out Chicago entries in OSHA's database
                newdatabase.append(case)
        database = newdatabase

    for case1 in database:
        if case1['hourvoice_id'] in visited:    # check if case1 has already been added
            continue
        for case2 in database:
            if case2['hourvoice_id'] in visited:    # check if case2 has already been added
                continue
            if cmp(case1,case2) != 0:   # make sure we're not looking at identical violations/cases
                if dba_header in case1 and dba_header in case2:
                    c1_name = case1[dba_header]
                    c2_name = case2[dba_header]
                    c1_hv_id = case1["hourvoice_id"]
                    c2_hv_id = case2["hourvoice_id"]

                    if c1_hv_id not in consolidated_data:
                        create_new_entry(consolidated_data, c1_hv_id, case1, repeated_headers, unique_headers)

                    if compare_lats_lons_and_dbaname(case1, case2, lat_header, lon_header, c1_name, c2_name):
                        for unique_header in unique_headers:
                            if unique_header in case2:
                                consolidated_data[c1_hv_id][unique_header].append(case2[unique_header])
                        visited.add(case2['hourvoice_id'])
        visited.add(case1['hourvoice_id'])
    return consolidated_data

# counts the number of violations that has been recorded of each business, and notes
# crossover between
def count_frequency(db1, db1_name, db1_dbaheader, db1_unique_header, db2, db2_name, db2_dbaheader, db2_unique_header):
    frequency_data = {}
    visited = set()
    for case1 in db1:
        if case1 in visited:    # check if case1 has already been added
            continue
        frequency_data[case1] = {}
        frequency_data[case1][db1_name] = db1[case1]
        frequency_data[case1]["Frequency"] = len(frequency_data[case1][db1_name][db1_unique_header])
        for case2 in db2:
            if case2 in visited:    # check if case2 has already been added
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


food_json = consolidate_data_by_hv_id(unique_food_headers, repeated_food_headers, 'dba_name', 'latitude', 'longitude', food_inspection_data)
osha_json = consolidate_data_by_hv_id(unique_osha_headers, repeated_osha_headers, 'Employer', 'Latitude', 'Longitude', osha_injury_data)

business_json = consolidate_data_by_hv_id(unique_business_headers, repeated_business_headers, 'doing_business_as_name', 'latitude', 'longitude', business_license_data)
sub_combined_databases = count_frequency(food_json, "food_inspection", 'dba_name', 'inspection_date', osha_json, "OSHA", 'Employer', 'ID')

# creates the finalized combined database with business_license data, food_inspection data, and OSHA data
combined_databases = {}
for case1 in business_json:
    combined_databases[case1] = {"business_license": business_json[case1]}
    for case2 in sub_combined_databases:
        align_score = 0
        if 'food_inspection' in sub_combined_databases[case2]:
            align_score = align_strings(business_json[case1]['doing_business_as_name'], sub_combined_databases[case2]['food_inspection']['dba_name'])[0]
        if 'OSHA' in sub_combined_databases[case2]:
            align_score = align_strings(business_json[case1]['doing_business_as_name'], sub_combined_databases[case2]['OSHA']['Employer'])[0]
        if align_score > score_thresh:
            combined_databases[case1].update(sub_combined_databases[case2])
        else:
            combined_databases[case2] = sub_combined_databases[case2]

output_file = open("combined_data.json", 'w')
output_file.write(json.dumps(combined_databases))
