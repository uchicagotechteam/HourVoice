import json

# global num_with_freq, biz, osha, only_food_inspection
# num_with_freq, biz, osha, only_food_inspection = 0,0,0,0

def get_subset(hourvoice_id, establishment):
    # global num_with_freq, biz, osha, only_food_inspection
    subset = {'hourvoice_id': hourvoice_id, 'name': '', 'address': '', 'frequency': '', 'owner': '', 'business_license_number': '', 'zip_code': '', 'city': ''}
    if 'Frequency' in establishment:
        subset['frequency'] = establishment['Frequency']
        # num_with_freq += 1
    if 'business_license' in establishment:
        # biz += 1
        subset['address'] = establishment['business_license']['address']
        subset['name'] = establishment['business_license']['doing_business_as_name']
        subset['zip_code'] = establishment['business_license']['zip_code']
        subset['city'] = establishment['business_license']['city']
    elif 'OSHA' in establishment:
        # osha += 1
        subset['name'] = establishment['OSHA']['Employer']
        subset['zip_code'] = establishment['OSHA']['Zip']
        subset['city'] = establishment['OSHA']['City']
    elif 'food_inspection' in establishment:
        # only_food_inspection += 1
        subset['name'] = establishment['food_inspection']['dba_name']
        subset['zip_code'] = establishment['food_inspection'].get('zip','')
        subset['address'] = establishment['food_inspection']['address']
        subset['city'] = establishment['food_inspection'].get('city','')
    # print(num_with_freq, biz, osha, only_food_inspection)
    return subset

if __name__ == '__main__':
    database = None
    with open('combined_data.json') as f:
        database = json.load(f)
    # database_glimpse = [get_subset(hv_id, data) for (hv_id, data) in database.items()]
    for hv_id in database.keys():
        glimpse = get_subset(hv_id, database[hv_id])
        database[hv_id]['glimpse'] = glimpse
    with open('combined_data_with_glimpse.json', 'w') as f:
        # json.dump(database_glimpse, f)
        json.dump(database, f, indent=2)
