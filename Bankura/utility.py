import pandas as pd
import psycopg2
import json, pprint, decimal, datetime, re
from collections import OrderedDict

def save_district_ac(dist_name):
    import json
    with open('../datasets/ac-shapes/wb_ac_shapes.json') as f:
        ac = json.load(f)

    features = [x for x in ac['features'] if x['properties']
                ['DIST_NAME'] == dist_name.upper()]
    ac['features'] = features

    with open('{}_ac_shapes.json'.format(dist_name), 'w') as f:
        json.dump(ac, f, indent=4)

def get_district_ac(dist_name):
    import json
    with open('../datasets/ac-shapes/wb_ac_shapes.json') as f:
        ac = json.load(f)

    features = [x for x in ac['features'] if x['properties']
                ['DIST_NAME'] == dist_name.upper()]
    ac['features'] = features

    return ac

def save_mouzas_of_district(dist_name):
    import json
    import pandas as pd
    from shapely.geometry import Polygon, Point

    # Load the ac-shapes for the district
    with open('{}_ac_shapes.json'.format(dist_name), 'r') as f:
        dist_ac = json.load(f)

    # Make a list of (object_id, polygons) for each ac in the dist
    ac_polygons = []
    for ac in dist_ac['features']:
        '''
        1. Poly-points is a list of tuples where
        each tuple is (long, lat) defining the
        boundary of the ac
        2. Object id is a unique id for each ac in India
        '''
        poly_points = [tuple(p) for p in ac['geometry']['coordinates'][0]]
        objectid = ac['properties']['OBJECTID']

        ac_polygons.append((objectid, Polygon(poly_points)))

    # Load all the mouza points
    mouzas = pd.read_csv('../datasets/processed/mouzas.csv')
    # dist_mouzas = pd.DataFrame([], columns=['name', 'jl_number', 'longitude', 'latitude', 'ac_id'])
    dist_mouzas = []

    # Check for each mouza
    for idx, mouza in mouzas.iterrows():
        print('\r Checking Mouza no {0} out of {1} Mouzas {2:02f}% complete\r'.format(
            idx, mouzas.shape[0], (idx + 1) / mouzas.shape[0] * 100.0), end='')
        mouza_point = Point(mouza['longitude'], mouza['latitude'])
        for oid, ac_poly in ac_polygons:
            if ac_poly.contains(mouza_point):
                dist_mouzas.append({
                    'id': mouza['id'],
                    'name': mouza['name'],
                    'longitude': mouza['longitude'],
                    'latitude': mouza['latitude'],
                    'jl_number': mouza['jl_number'],
                    'ac_id': oid,
                })
                break

    pd.DataFrame(dist_mouzas)[['id', 'name', 'jl_number', 'longitude', 'latitude', 'ac_id']].to_csv(
        '{}_mouzas.csv'.format(dist_name), index=False)
    print('\nMouzas Saved')

def process_data_row(data):
    popkeys = []
    for key, item in data.items():
        if type(item) is decimal.Decimal:
            data[key] = float(item)
        elif (type(item) is datetime.datetime) or (type(item) is datetime.date):
            popkeys.append(key)
        elif (key == 'kharif_crops' or key == 'pre_kharif_crops' or key == 'rabi_crops') and item is not None and type(item) is str:
            crop = [int(x) for x in re.split('- |, |\n',item) if x.isdigit()]
            data[key] = crop
    for key in popkeys:
        data.pop(key, None)
    return data

def save_soil_sample(dist_name):

    with open('../config.json', 'r') as f:
        params = json.load(f)
    connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(params['dbname'], params['user'], params['host'], params['password'])
    conn = psycopg2.connect(connect_str)

    # Get Soil Sample col names
    cursor = conn.cursor()
    cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{0}';
            """.format('soil_samples'))
    soil_sample_cnames = cursor.fetchall()
    soil_sample_cnames = [x[0] for x in soil_sample_cnames]


    # Find samples for each mouza
    mouzas = pd.read_csv('{}_mouzas.csv'.format(dist_name))
    soil_sample_dict = {}
    count = 0
    for idx, mouza in mouzas.iterrows():
        cursor.execute("""
                SELECT *
                FROM soil_samples
                WHERE mouza_id = {0}
                ORDER BY sample_id;
                """.format(mouza['id']))
        soil_samples = [dict(zip(soil_sample_cnames, row)) for row in cursor.fetchall()]
        soil_samples = [process_data_row(row) for row in soil_samples]

        soil_sample_dict[mouza['id']] = soil_samples
        count += len(soil_samples)


    # Save the soil_samples
    with open('{}_soil_samples.json'.format(dist_name), 'w') as f:
        json.dump(OrderedDict(sorted(soil_sample_dict.items())), f, indent=4)

if __name__ == '__main__':
    # mouzas = pd.read_csv('{}_mouzas.csv'.format('bankura'))
    # soil_sample_list = []
    # for mouza in mouzas.iterrows():
    #     print(mouza)
    save_soil_sample('bankura')
