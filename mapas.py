import json 
import pandas as pd
import pydeck as pdk
import streamlit  as st

import pydeck as pdk

municipios_yucatan = "Yucatan.geojson"
with open(municipios_yucatan) as archivo:
    municipios_json = json.load(archivo)
dfMunicipios = pd.read_csv("municipiosDatos.csv")
dfMunicipios.drop('Unnamed: 0',axis=1,inplace=True)
st.dataframe(dfMunicipios)

# Create a copy of the GeoJSON data to modify it
enriched_municipios_json = json.loads(json.dumps(municipios_json))

# Merge RandomNumbers from dfMunicipios into the GeoJSON properties
for feature in enriched_municipios_json['features']:
    municipio_name = feature['properties']['NOMGEO']
    # Find the corresponding row in dfMunicipios
    matching_row = dfMunicipios[dfMunicipios['Municipio'] == municipio_name]
    if not matching_row.empty:
        # Convert numpy.int64 to a standard Python int
        random_number = int(matching_row['RandomNumbers'].iloc[0])
        feature['properties']['RandomNumbers'] = random_number
    else:
        feature['properties']['RandomNumbers'] = 0 # Default value if no match found
# Define the pydeck GeoJsonLayer
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    enriched_municipios_json,
    filled=True,
    get_fill_color=[
        "(properties.RandomNumbers / 1000) * 255", # Red component (scaled by value)
        "(properties.RandomNumbers / 1000) * 255", # Green component
        "255 - (properties.RandomNumbers / 1000) * 255", # Blue component (inverse scaled)
        200 # Alpha transparency
    ],
    get_line_color=[0, 0, 0, 200],
    get_line_width=1,
    stroked=True,
    opacity=0.8,
    extruded=False,
    auto_highlight=True,
    pickable=True # Make polygons pickable for interactivity
)

# Set the initial view state for Yucatan
view_state = pdk.ViewState(
    latitude=20.8,
    longitude=-89.0,
    zoom=7,
    pitch=0
)

# Create the pydeck Deck
r = pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=view_state,
    tooltip={"text": "Municipio: {NOMGEO}\nRandomNumbers: {RandomNumbers}"}
)

# Render the deck

st.pydeck_chart(r)


