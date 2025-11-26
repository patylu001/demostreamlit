import json 
import pandas as pd
import plotly.express as px
import streamlit  as st

municipios_yucatan = "Yucatan.geojson"
with open(municipios_yucatan) as archivo:
    municipios_json = json.load(archivo)

dfMunicipios = pd.read_csv("municipiosDatos.csv")

fig = px.choropleth(dfMunicipios, geojson=municipios_json, locations='Municipio',
                    color='RandomNumbers',
                    color_continuous_scale="Viridis",
                    range_color=(0, 10000),
                    featureidkey="properties.NOMGEO",
                    labels={'RandomNumbers':'Votos'} )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  geo_center={"lat": 20.8, "lon": -89.0}, # Approximate center of Yucatan
                  geo_scope="north america", # Limit the scope to North America
                  geo_projection_scale=7 # Adjust zoom level as needed using the correct property
                 )

st.plotly_chart(fig, use_container_width=True)
