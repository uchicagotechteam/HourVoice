import json, urllib, csv
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))
from csv_to_json import convert_csv_to_json
from align_strings import align_strings

score_thresh = 0.8 # for name comparisons/alignments
unique_food_headers = ['results, inspection_id', 'license_', 'violations', 'risk', 'inspection_type', 'inspection_date', ]
repeated_food_headers = [':@computed_region_bdys_3d7i', ':@computed_region_43wa_7qmu', ':@computed_region_6mkv_f3dw', ':@computed_region_awaf_s7ux', ':@computed_region_vrxf_vc4k', 'dba_name', 'city', 'zip', 'facility_type', 'state', 'location', 'latitude', 'aka_name', 'address', 'longitude']
unique_osha_headers = ['Part of Body', 'Source', 'Final Narrative', 'Nature', 'Hospitalized', 'Primary NAICS', 'Amputation', 'Secondary Source', 'Part of Body Title', 'Secondary Source Title', 'Inspection', 'ID', 'EventTitle', 'SourceTitle', 'EventDate', 'NatureTitle', 'Event', 'UPA']
repeated_osha_headers = ['City', 'Zip', 'Employer', 'State', 'Latitude', 'Longitude', 'Address1', 'Address2']

# osha = open("severeinjury.csv", 'r+')
# osha_text = unicode(osha.read(), errors = 'ignore')
# osha.write(osha_text)
# osha.close()

#convert_csv_to_json("Business_Licenses.csv", "Business_License.json", "DOING BUSINESS AS NAME")
#convert_csv_to_json("severeinjury.csv", "severeinjury.json", "Employer")

def load_file(file_name):
    file = open(file_name, 'r')
    return json.loads(file.read())

food_inspection_data = load_file("cityofchicagofood.json")
osha_injury_data = load_file("severeinjury.json")
#business_license_data = load_file("Business_License.json")

def group_data_by_dbaname(unique_headers, repeated_headers, dba_header, lat_header, lon_header, database):
    found = {}
    for case1 in database:
        for case2 in database:
            if cmp(case1,case2) != 0:
                lats_included = lat_header in case1 and lat_header in case2
                lons_included = lon_header in case1 and lon_header in case2
                lats_match = case1[lat_header] == case2[lat_header]
                lons_match = case2[lon_header] == case1[lon_header]
                if lats_included and lons_included and lats_match and lons_match:
                        if dba_header in case1 and dba_header in case2:
                            c1_name = case1[dba_header]
                            c2_name = case2[dba_header]
                            align_score = align_strings(c1_name, c2_name)[0]
                            if c1_name not in found:
                                found[c1_name] = {}
                                for repeat_header in repeated_headers:
                                    if repeat_header in case1:
                                        found[c1_name].update({repeat_header: case1[repeat_header]})
                                for unique_header in unique_headers:
                                    if unique_header in case1:
                                        found[c1_name].update({unique_header: [case1[unique_header]]})
                                    else:
                                        found[c1_name][unique_header] = []
                            if align_score > score_thresh:
                                for unique_header in unique_headers:
                                    if unique_header in case2:
                                        found[c1_name][unique_header].append(case2[unique_header])
    return found

food_json = group_data_by_dbaname(unique_food_headers, repeated_food_headers, 'dba_name', 'latitude', 'longitude', food_inspection_data)
osha_json = group_data_by_dbaname(unique_osha_headers, repeated_osha_headers, 'Employer', 'Latitude', 'Lonngitude', osha_injury_data)

print osha_json

output_file = open("output.txt", 'w')
output_file.write(json.dumps(food_json))
output_file.write(json.dumps(osha_json))

biz_data = [d[0].split(',') for d in all_chicago_businesses[:1000] if len(d[0].split(',')) == len(chicago_business_headers)]

#fixes formatting error for missing data
for business in biz_data:
	if isFloat(business[latitude_chibiz]):
		business[latitude_chibiz] = float(business[latitude_chibiz])
	else:
		business[latitude_chibiz] = 0.0
	if isFloat(business[longitude_chibiz]):
		business[longitude_chibiz] = float(business[longitude_chibiz])
	else:
		business[longitude_chibiz] = 0.0

def compileDataWithFrequencies():
	(cross_refed, osha_data_chicago) = crossReferenceDatabases()
	dba_name_chibiz = []
	final1 = []
	final = ""
	for i in osha_data_chicago:
		if isFloat(i[9]) and isFloat(i[10]):
			i[9] = str(i[9])
			i[10] = str(i[10])
	for item in cross_refed:
		dba_name_chibiz.append(item[0])
	for i in cross_refed:
		bulk = [[str(dba_name_chibiz.count(i[0]))] + i[1] + i[2] + i[3]]
		final1.append(bulk)
	for j in final1:
		final = final + (','.join(j[0])) + '\n'
	return final
