import json, urllib, csv
from collections import defaultdict
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))

from align_strings import align_strings

score_thresh = 0.8 # for name comparisons/alignments

food_inspection_file = open("cityofchicagofood.json", 'r')
food_inspection_data = json.loads(food_inspection_file.read())
food_headers = [x[0] for x in food_inspection_data[1].items()]

#food_headers = [u'dba_name', u'results', u':@computed_region_6mkv_f3dw', u':@computed_region_bdys_3d7i', u'city', u'zip', u'facility_type', u'state', u'inspection_id', u'license_', u'location', u'latitude', u'violations', u'aka_name', u'risk', u'inspection_type', u':@computed_region_awaf_s7ux', u':@computed_region_43wa_7qmu', u'address', u'inspection_date', u':@computed_region_vrxf_vc4k', u'longitude']

unique_food_headers = ['results, inspection_id', 'license_', 'violations', 'risk', 'inspection_type', 'inspection_date', ]
repeated_food_headers = [':@computed_region_bdys_3d7i', ':@computed_region_43wa_7qmu', ':@computed_region_6mkv_f3dw', ':@computed_region_awaf_s7ux', ':@computed_region_vrxf_vc4k', 'dba_name', 'city', 'zip', 'facility_type', 'state', 'location', 'latitude', 'aka_name', 'address', 'longitude']

found = {}

for case1 in food_inspection_data:
    for case2 in food_inspection_data:
        if cmp(case1,case2) != 0:
            if 'latitude' in case1 and 'latitude' in case2 and 'longitude' in case1 and 'longitude' in case2 and case1['latitude'] == case2['latitude'] and case2['longitude'] == case1['longitude']:
                    if 'dba_name' in case1 and 'dba_name' in case2:
                        food_align_score = align_strings(case1['dba_name'], case2['dba_name'])[0]
                        if food_align_score > score_thresh:
                            found[(case1['dba_name'])] = {}
                            for repeat_header in repeated_food_headers:
                                if repeat_header in case1:
                                    found[(case1['dba_name'])].update({repeat_header: case1[repeat_header]})
                            for unique_header in unique_food_headers:
                                if unique_header in case1 and unique_header in case2:
                                    found[(case1['dba_name'])].update({unique_header: [case1[unique_header], case2[unique_header]]})

all_chicago_businesses = [row for row in csv.reader(open("Business_Licenses.csv", 'r'), delimiter='"')]
chicago_business_headers = all_chicago_businesses[0][0].split(',')

osha_data = [row for row in csv.reader(open("severeinjury.csv", 'r'))]
osha_headers = osha_data[0]

output_file = open("output.txt", 'w')
output_file.write(json.dumps(found))
#giving the output file headers
# output_file.write("Frequency,"
#                  + all_chicago_businesses[0][0]
# 				 + ", "
# 				 + ','.join(osha_headers)
# 				 + ", "
# 				 +','.join([x[0] for x in food_inspection_data[0].items() if not (type(x[0]) is dict)]) + "\n")

# separates the key info by commas
biz_data = [d[0].split(',') for d in all_chicago_businesses[:1000] if len(d[0].split(',')) == len(chicago_business_headers)]

# returns the index of the desired header
def getHeaderIndex(headers, header):
	for i in range(len(headers)):
		if headers[i] == header:
			return i

def getCSVDataByHeader(data, headers, header):
	head = getHeaderIndex(headers, header)
	return [d[head] for d in data]

def getJSONDataByHeader(data, header):
	return [d[header] for d in data if (header in d)]

def toLower(data):
	return data.lower()

def roundMapOSHA(data):
	return round(data, 2)

def roundMapFood(data):
	return round(data, 6)

def isFloat(str):
        try:
        	float(str)
        	return True
        except ValueError:
            return False

#import indices
latitude_chibiz  = getHeaderIndex(chicago_business_headers, "LATITUDE")
longitude_chibiz = getHeaderIndex(chicago_business_headers, "LONGITUDE")
dba_name_chibiz  = getHeaderIndex(chicago_business_headers, "DOING BUSINESS AS NAME")
dba_name_osha    = getHeaderIndex(osha_headers, "Employer")

#latitudes and longitudes for osha and food inspection database
food_lats = map(roundMapFood, map(float, getJSONDataByHeader(food_inspection_data, 'latitude')))
food_lons = map(roundMapFood, map(float, getJSONDataByHeader(food_inspection_data, 'longitude')))
osha_lats = getCSVDataByHeader(osha_data, osha_headers, 'Latitude')[1:]
osha_lons = getCSVDataByHeader(osha_data, osha_headers, 'Longitude')[1:]

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

def getOSHAChicago():
	osha_cities  = getCSVDataByHeader(osha_data, osha_headers, 'City')
	indices = [i for i in range(len(osha_cities)) if (osha_cities[i] == 'CHICAGO')]
	osha_chicago_lons = [(osha_lons[j],j) for j in indices]
	osha_chicago_lats = [(osha_lats[j],j) for j in indices]
	return (osha_chicago_lats, osha_chicago_lons)

def crossReferenceDatabases():
	compared_data = []
	osha_data_chicago = formatLatsAndLons()
	for business in biz_data:
		for osha_case in osha_data_chicago:
			align_score = align_strings(business[dba_name_chibiz], osha_case[dba_name_osha])[0]
			same_name = align_score > score_thresh
			if same_name:
				business[latitude_chibiz] = str(business[latitude_chibiz])
				business[longitude_chibiz] = str(business[longitude_chibiz])
				osha_case[9] = str(osha_case[9])
				osha_case[10] = str(osha_case[10])
				compared_data.append((business[dba_name_chibiz], business, osha_case, []))
	for business in biz_data:
		blats = round(float(business[latitude_chibiz]),6)
		blons = round(float(business[longitude_chibiz]),6)
		if (blats in set(food_lats)) and (blons in set(food_lons)):
			for food_inspection_case in food_inspection_data:
				if 'latitude' and 'longitude' in food_inspection_case:
					if round(float(food_inspection_case['latitude']),6) == blats and round(float(food_inspection_case['longitude']),6) == blons:
						business[latitude_chibiz] = str(business[latitude_chibiz])
						business[longitude_chibiz] = str(business[longitude_chibiz])
						food_inspection_case['latitude'] = str(food_inspection_case['latitude'])
						food_inspection_case['longitude'] = str(food_inspection_case['longitude'])
						bulk = [x[1] for x in food_inspection_case.items() if not (type(x[1]) is dict)]
						compared_data.append((business[dba_name_chibiz],business,[],bulk))
	return (compared_data, osha_data_chicago)

def formatLatsAndLons():
    biz_at_lat = []
    (osha_chicago_lats, osha_chicago_lons) = getOSHAChicago()
    formatted_osha_chicago_lats = []
    formatted_osha_chicago_lons = []
    osha_data_chicago = []
    for i in osha_chicago_lats:
        formatted_osha_chicago_lats.append(float(i[0]))
        if isFloat(osha_data[i[1]][9]) and isFloat(osha_data[i[1]][10]):
            osha_data[i[1]][9]  = float(osha_data[i[1]][9])
            osha_data[i[1]][10] = float(osha_data[i[1]][10])
        osha_data_chicago.append(osha_data[i[1]])
    for j in osha_chicago_lons:
        formatted_osha_chicago_lons.append(float(j[0]))
    # for business in biz_data:
    #     blats = round(float(business[longitude_chibiz]),2)
    #     blons = round(float(business[longitude_chibiz]),2)
    #     if (blats in set(formatted_osha_chicago_lats)) and (blons in set(formatted_osha_chicago_lons)):
    #         for j in osha_data_chicago:
    #             same_coords = (j[9] == blats and j[10] == blons)
    #             align_score = align_strings(business[dba_name_chibiz], j[dba_name_osha])[0]
    #             same_name = align_score > score_thresh
    #             if same_coords and same_name:
    #                 business[latitude_chibiz] = str(business[latitude_chibiz])
    #                 business[longitude_chibiz] = str(business[longitude_chibiz])
    #                 j[9] = str(j[9])
    #                 j[10] = str(j[10])
    #                 biz_at_lat.append((i[latitude_chibiz], (business[dba_name_chibiz], business, j, [])))
    return osha_data_chicago

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

formatLatsAndLons()
