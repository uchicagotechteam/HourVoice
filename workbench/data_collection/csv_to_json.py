import csv
import json

def read_csv_as_dict(file_name, primary_key):
    '''@param primary_key: string, name of unique identifying field in csv'''
    result = dict()
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row[primary_key]
            result[key] = row
    return result

def convert_csv_to_json(csv_file, json_file, primary_key):
    '''@param primary_key: string, name of unique identifying field in csv'''
    result = read_csv_as_dict(csv_file, primary_key)
    with open(json_file, 'w') as f:
        json.dump(result, f)
    return

if __name__ == '__main__':
    convert_csv_to_json('output.txt', 'output.json', primary_key='ID')
