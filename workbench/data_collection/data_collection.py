import json, urllib, csv
import os
import sys
sys.path.insert(0, os.path.abspath('../../disambiguation'))

from align_strings import align_strings

score_thresh = 0.7 # for name comparisons/alignments

food_inspection_file = open("cityofchicagofood.json", 'r')
food_inspection_data = json.loads(food_inspection_file.read())

all_chicago_businesses = [row for row in csv.reader(open("Business_Licenses.csv", 'r'), delimiter='"')]
chicago_business_headers = all_chicago_businesses[0][0].split(',')

osha_data = [row for row in csv.reader(open("severeinjury.csv", 'r'))]
osha_headers = osha_data[0]

output_file = open("output.txt", 'w')

#giving the output file headers
output_file.write("Frequency,"
                 + all_chicago_businesses[0][0]
				 + ", "
				 + ','.join(osha_headers)
				 + ", "
				 +','.join([x[0] for x in food_inspection_data[0].items() if not (type(x[0]) is dict)]) + "\n")

# separates the key info by commas
biz_data = [d[0].split(',') for d in all_chicago_businesses[:500] if len(d[0].split(',')) == len(chicago_business_headers)]

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
	(biz_at_lat, oshadata) = findAllAtLatsAndLons()
	for business in biz_data:
		for osha_case in oshadata:
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
	return (compared_data, oshadata)

def findAllAtLatsAndLons():
    biz_at_lat = []
    (oshalats, oshalons) = getOSHAChicago()
    oshalaforcomp = []
    oshaloforcomp = []
    oshadata = []
    for i in oshalats:
        oshalaforcomp.append(float(i[0]))
        if isFloat(osha_data[i[1]][9]) and isFloat(osha_data[i[1]][10]):
            osha_data[i[1]][9]  = float(osha_data[i[1]][9])
            osha_data[i[1]][10] = float(osha_data[i[1]][10])
        oshadata.append(osha_data[i[1]])
    for j in oshalons:
        oshaloforcomp.append(float(j[0]))
    for i in biz_data:
        blats = round(float(i[longitude_chibiz]),2)
        blons = round(float(i[longitude_chibiz]),2)
        if (blats in set(oshalaforcomp)) and (blons in set(oshaloforcomp)):
            for j in oshadata:
                same_coords = (j[9] == blats and j[10] == blons)
                if "university" in i[dba_name_chibiz].lower() and "university" in j[dba_name_osha].lower():
	            	print align_strings(i[dba_name_chibiz], j[dba_name_osha])
                align_score = align_strings(i[dba_name_chibiz], j[dba_name_osha])[0]
                same_name = align_score > score_thresh
                if same_coords and same_name:
                    i[latitude_chibiz] = str(i[latitude_chibiz])
                    i[longitude_chibiz] = str(i[longitude_chibiz])
                    j[9] = str(j[9])
                    j[10] = str(j[10])
                    biz_at_lat.append((i[latitude_chibiz], (i[dba_name_chibiz], i, j, [])))
    return (biz_at_lat, oshadata)

def compileDataWithFrequencies():
	(cross_refed, oshadata) = crossReferenceDatabases()
	dba_name_chibiz = []
	final1 = []
	final = ""
	for i in oshadata:
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

findAllAtLatsAndLons()
output_file.write(compileDataWithFrequencies())
