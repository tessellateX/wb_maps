import pandas as pd
import folium, os
result = pd.read_csv('datasets/processed/final.csv')
wb_map = folium.Map(location=[22.9964948,87.6855882],  zoom_start=6.5, width='100%', height=800,)
for idx, row in result.iterrows():
    print('Percentage loaded {0:.3f}\r'.format(idx*100.0/result.shape[0]), end='')
    folium.Circle(
        radius=50,
        location=[row['latitude'], row['longitude']],
        popup='<i>{}</i>'.format(row['name']),
        color='crimson',
        fill=True,
    ).add_to(wb_map)
    # folium.Marker([row['latitude'], row['longitude']], popup='<i>{}</i>'.format(row['name'])).add_to(wb_map)
folium.GeoJson(
    os.path.join('./', 'datasets/ac-shapes/wb-ac-shapes.json'),
    name='geojson'
).add_to(wb_map)

wb_map.save('index.html')
