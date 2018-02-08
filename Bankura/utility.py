def save_district_ac(dist_name):
    import json
    with open('../datasets/ac-shapes/wb-ac-shapes.json') as f:
        ac = json.load(f)

    features = [x for x in ac['features'] if x['properties']['DIST_NAME'] == dist_name.upper()]
    ac['features'] = features

    with open('{}-ac-shapes.json'.format(dist_name), 'w') as f:
        json.dump(ac, f, indent=4)

def get_district_ac(dist_name):
    import json
    with open('../datasets/ac-shapes/wb-ac-shapes.json') as f:
        ac = json.load(f)

    features = [x for x in ac['features'] if x['properties']['DIST_NAME'] == dist_name.upper()]
    ac['features'] = features

    return ac

def save_mouzas_of_district(dist_name):
    import json
    import pandas as pd
    from shapely.geometry import Polygon, Point

    # Load the ac-shapes for the district
    with open('{}-ac-shapes.json'.format(dist_name), 'r') as f:
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
        print('\r Checking Mouza no {0} out of {1} Mouzas {2:02f}% complete\r'.format(idx, mouzas.shape[0], (idx+1)/mouzas.shape[0]*100.0), end='')
        mouza_point = Point(mouza['longitude'], mouza['latitude'])
        for oid, ac_poly in ac_polygons:
            if ac_poly.contains(mouza_point):
                dist_mouzas.append({
                    'id':mouza['id'],
                    'name':mouza['name'],
                    'longitude':mouza['longitude'],
                    'latitude':mouza['latitude'],
                    'jl_number':mouza['jl_number'],
                    'ac_id':oid,
                })
                break

    pd.DataFrame(dist_mouzas)[['id', 'name', 'jl_number', 'longitude', 'latitude', 'ac_id']].to_csv('{}_mouzas.csv'.format(dist_name), index=False)
    print('\nMouzas Saved')

if __name__ == '__main__':
    save_mouzas_of_district('bankura')
