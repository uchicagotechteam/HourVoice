import json
from collections import defaultdict

def combine_databases(databases, compared_keys, equality_functions, database_names):
    '''
    @param databases: a list of dicts, where each dict's values should be
    dictionaries mapping headers to individual data points. For example, [db1, db2] with db1 = {'1': , '2': {'name': 'bar'}}
    @param compared_keys: a list of lists of corresponding keys to compare.
    For example, [['name', 'db_name']] would match solely based on comparing
    the 'name' column of db1 and the 'db_name' column of db2
    @param database_names: corresponding names to assign to each database
    @param equality_functions: binary equality testing functions for each
    corresponding index of compared_keys, each should return a boolean
    @return: a combined dict of all the data, using the primary key of the
    first database as the primary key for the result. For example, with
    database_names = ['db1', 'db2'], data = {'1': {'db1': {'name': 'foo'},
    'db2': {'db_name': 'Foo'}}, '2': {'db1': {'name': 'bar'}, 'db2':
    {'db_name': 'Baz'}}
    Note: all comparisons are done to the first database
    '''
    n = len(databases)
    if not n:
        return dict()
    result = defaultdict(dict)
    for (key, data) in databases[0].items():
        result[key][database_names[0]] = data
    for (db_keys, equal) in zip(compared_keys, equality_functions):
        for base_name in databases[0].keys():
            base_value = databases[0][base_name][db_keys[0]]
            for i in range(1,n):
                for (name, data) in databases[i].items():
                    test_value = data[db_keys[i]]
                    if equal(base_value, test_value):
                        result[base_name][database_names[i]] = data
    return result
    # for name in databases[0].keys():
        # result[name] = {db_name: dict() for db_name in database_names}

if __name__ == '__main__':
    db1 = {'A': {'name': 'A', 'id': 1}, 'B': {'name': 'B', 'id': 2}}
    db2 = {'Ark': {'name2': 'Ark', 'desc': 'I like Noah'}, 'Boo': {'name2': 'Boo', 'desc': 'I like to scare Noah'}}
    combined = combine_databases(
        databases=[db1, db2],
        compared_keys=[['name', 'name2']],
        equality_functions=[lambda x,y: x[0]==y[0]],
        database_names=['DB1', 'DB2'])
    print(combined)
