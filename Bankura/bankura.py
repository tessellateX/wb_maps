import json
import folium
import pandas as pd
from shapely.geometry import Polygon, Point
with open('../datasets/ac-shapes/wb-ac-shapes.json') as f:
    ac = json.load(f)

features = [x for x in ac['features'] if x['properties']['DIST_NAME'] == 'BANKURA']
ac['features'] = features
wb_map = folium.Map(location=[22.9964948,87.6855882],  zoom_start=6.5, width='100%', height='100%',)

folium.GeoJson(
    ac,
    name='geojson'
).add_to(wb_map)




polygons = []
for x in features:
    poly_points = x['geometry']['coordinates'][0]
    poly_points = [tuple(p) for p in poly_points]
    polygons.append(Polygon(poly_points))
#
#
result = pd.read_csv('../datasets/processed/final.csv')
for idx, row in result.iterrows():
    print('Percentage loaded {0:.3f}\r'.format(idx*100.0/result.shape[0]), end='')
    point = Point([row['longitude'], row['latitude']])
    for poly in polygons:
        if poly.contains(point):
            folium.Circle(
                radius=50,
                location=[row['latitude'], row['longitude']],
                popup='<i>{}</i>'.format(row['name']),
                color='crimson',
                fill=True,
            ).add_to(wb_map)
            break

print()
wb_map.save('bankura.html')
