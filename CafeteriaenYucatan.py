import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import plotly.express as px

# Load the modified Excel file
file_path = 'Coffee Shop Sales_Modified.xlsx'
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct location.")
    st.stop()

st.title("Cafeterías ubicadas en Yucatán ☕")

# Ensure 'store_name' column exists and 'state store location' was added
if 'store_location' in df.columns and 'store_name' not in df.columns:
    df.rename(columns={'store_location': 'store_name'}, inplace=True)

# Create a dictionary for state store location to lat/lon mapping
# Approximate coordinates for the specified locations in Yucatán, Mexico
location_coordinates = {
    'MOTUL': {'lat': 21.1667, 'lon': -89.2667},
    'TICUL': {'lat': 20.5833, 'lon': -89.5333},
    'MERIDA': {'lat': 20.9670, 'lon': -89.6247}
}

# Add 'latitude' and 'longitude' columns to the DataFrame
if 'state store location' in df.columns:
    # Ensure state store location column values are clean and in line with dictionary keys
    df['state store location'] = df['state store location'].str.upper().str.strip()
    df['latitude'] = df['state store location'].map(lambda x: location_coordinates.get(x, {}).get('lat'))
    df['longitude'] = df['state store location'].map(lambda x: location_coordinates.get(x, {}).get('lon'))
else:
    st.warning("Column 'state store location' not found. Cannot map store locations.")
    df['latitude'] = None
    df['longitude'] = None

# Drop rows where latitude or longitude could not be determined
df.dropna(subset=['latitude', 'longitude'], inplace=True)

# Load GeoJSON for municipalities (assuming Yucatan.geojson is in the root directory)
# and dfMunicipios.csv is also available
municipios_yucatan_path = 'Yucatan.geojson'
municipios_datos_path = 'municipiosDatos.csv'

try:
    with open(municipios_yucatan_path) as archivo:
        municipios_json = json.load(archivo)
    dfMunicipios = pd.read_csv(municipios_datos_path)
    dfMunicipios.drop('Unnamed: 0', axis=1, inplace=True)

    # Create a copy of the GeoJSON data to modify it
    enriched_municipios_json = json.loads(json.dumps(municipios_json))

    # Merge RandomNumbers from dfMunicipios into the GeoJSON properties
    for feature in enriched_municipios_json['features']:
        municipio_name = feature['properties']['NOMGEO']
        matching_row = dfMunicipios[dfMunicipios['Municipio'] == municipio_name]
        if not matching_row.empty:
            random_number = int(matching_row['RandomNumbers'].iloc[0])
            feature['properties']['RandomNumbers'] = random_number
        else:
            feature['properties']['RandomNumbers'] = 0  # Default value if no match found

    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        enriched_municipios_json,
        filled=True,
        get_fill_color=[
            "(properties.RandomNumbers / 1000) * 255",  # Red component (scaled by value)
            "(properties.RandomNumbers / 1000) * 255",  # Green component
            "255 - (properties.RandomNumbers / 1000) * 255",  # Blue component (inverse scaled)
            100  # Alpha transparency (reduced for better visibility of points)
        ],
        get_line_color=[0, 0, 0, 100],
        get_line_width=1,
        stroked=True,
        opacity=0.5,
        extruded=False,
        auto_highlight=True,
        pickable=True
    )
except FileNotFoundError:
    st.warning("GeoJSON or municipiosDatos.csv files not found. The base map will not be displayed.")
    geojson_layer = None


# Extract unique store names for filter options
unique_store_names = df['store_name'].unique().tolist() if 'store_name' in df.columns else []

# Extract unique product types for filter options
unique_product_types = df['product_type'].unique().tolist() if 'product_type' in df.columns else []

st.sidebar.header("Filter Data")

# Create a Streamlit multiselect widget in the sidebar for 'store_name'
selected_store_names = st.sidebar.multiselect(
    'Select Stores:',
    options=unique_store_names,
    default=unique_store_names
)

# Create a Streamlit multiselect widget in the sidebar for 'product_type'
selected_product_types = st.sidebar.multiselect(
    'Select Product Types:',
    options=unique_product_types,
    default=unique_product_types
)

# Apply filters to the DataFrame
filtered_df = df[
    df['store_name'].isin(selected_store_names) &
    df['product_type'].isin(selected_product_types)
]

st.subheader("Ubicación de las sucursales:")

if not filtered_df.empty:
    # Aggregate data to get unique store locations and their details
    store_locations_for_map = filtered_df[['store_name', 'state store location', 'latitude', 'longitude']].drop_duplicates()

    # Set the initial view state for the map, centered around the mean coordinates of all stores,
    # or a default view for Yucatan if no stores are selected.
    if not store_locations_for_map.empty:
        initial_latitude = store_locations_for_map['latitude'].mean()
        initial_longitude = store_locations_for_map['longitude'].mean()
        initial_zoom = 9 # Adjust zoom level as needed
    else:
        # Default view for Yucatan if no stores are selected or filtered
        initial_latitude = 20.8
        initial_longitude = -89.0
        initial_zoom = 7

    view_state = pdk.ViewState(
        latitude=initial_latitude,
        longitude=initial_longitude,
        zoom=initial_zoom,
        pitch=45
    )

    # Create a PyDeck Layer for the Scatterplot
    scatterplot_layer = pdk.Layer(
        'ScatterplotLayer',
        store_locations_for_map,
        get_position='[longitude, latitude]',
        get_color='[200, 30, 0, 160]',
        get_radius=500,  # Radius in meters
        pickable=True
        #tooltip={
        #    "text": "Store: {store_name}\nLocation: {state store location}\nLat: {latitude}\nLon: {longitude}"
        #}
    )

    # Combine layers
    layers_to_render = []
    if geojson_layer:
        layers_to_render.append(geojson_layer)
    layers_to_render.append(scatterplot_layer)

    # Create a Deck object
    r = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=layers_to_render,
        tooltip={
             "text": "Store: {store_name}\nLocation: {state store location}"
            #"html": "<b>Store:</b> {store_name}<br/><b>Location:</b> {state store location}"
        }
    )

    # Render the map
    st.pydeck_chart(r)
else:
    st.warning("No store locations to display based on current filters.")

st.subheader("Información de ventas:")
if not filtered_df.empty:
    st.dataframe(filtered_df)
else:
    st.warning("No data available for the selected filters.")

# --- New Chart: Most Sold Products ---
st.subheader("Productos más vendidos (filtrado):")
if not filtered_df.empty:
    top_products_filtered = filtered_df.groupby('product_detail')['transaction_qty'].sum().nlargest(10).reset_index()
    top_products_filtered.rename(columns={'transaction_qty': 'total_quantity_sold'}, inplace=True)

    fig_products = px.bar(
        top_products_filtered,
        x='product_detail',
        y='total_quantity_sold',
        title='Top 10 Productos más vendidos por cantidad',
        labels={'product_detail': 'Producto', 'total_quantity_sold': 'Cantidad Total Vendida'}
    )
    fig_products.update_layout(xaxis_title_standoff=25)
    fig_products.update_xaxes(tickangle=45)
    st.plotly_chart(fig_products, width='stretch')
else:
    st.warning("No hay datos de productos para mostrar con los filtros seleccionados.")

# --- New Chart: Hourly Traffic ---
st.subheader("Afluencia por horas (filtrado):")
if not filtered_df.empty:
    # Ensure 'transaction_time' is in datetime format to extract hour
    df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%H:%M:%S').dt.time # Convert to just time objects for consistency if it's mixed with dates
    
    # Extract hour from transaction_time, handle if it's already a time object
    # Need to re-process filtered_df to ensure 'hour' column is available
    filtered_df_with_hour = filtered_df.copy()
    filtered_df_with_hour['hour'] = pd.to_datetime(filtered_df_with_hour['transaction_time'], format='%H:%M:%S').dt.hour

    hourly_traffic = filtered_df_with_hour.groupby('hour')['transaction_id'].count().reset_index()
    hourly_traffic.rename(columns={'transaction_id': 'number_of_transactions'}, inplace=True)

    fig_hourly = px.line(
        hourly_traffic,
        x='hour',
        y='number_of_transactions',
        title='Número de Transacciones por Hora',
        labels={'hour': 'Hora del Día', 'number_of_transactions': 'Número de Transacciones'}
    )
    fig_hourly.update_layout(xaxis = dict(tickmode = 'linear', dtick = 1))
    st.plotly_chart(fig_hourly, width='stretch')
else:
    st.warning("No hay datos de afluencia para mostrar con los filtros seleccionados.")


# Custom CSS for the Streamlit app
# We apply the body background directly to the Streamlit main container (.stApp)
# And create classes for the content box and stickers
custom_css = """
<style>
    /* Apply beige background to the entire Streamlit app */
    .stApp {
        background-color: #F5F5DC; /* Código hexadecimal para beige */
        font-family: Arial, sans-serif;
        color: #333;
    }
    /* Style for the content box */
    .content-box {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-top: 50px; /* Adjust as needed for vertical spacing */
        margin-bottom: 50px;
        max-width: 600px; /* Limit width for better presentation */
        margin-left: auto;
        margin-right: auto;
    }
    /* Style for the sticker container */
    .sticker-container {
        margin-top: 20px;
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    /* Style for individual stickers */
    .sticker {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 50%; /* Para darle forma de sticker redondo */
        border: 3px solid #f0e68c; /* Borde beige claro */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
</style>
"""

# Inject custom CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Main content box using a Streamlit container and custom HTML div
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.title("¡Gracias por tu visita!")
    st.write("Esperamos que regreses muy pronto!!")

    st.image("https://github.com/maricielonavarro31-ops/streamlit-example/blob/master/Good%20Morning%20Cat%20Sticker%20by%20Raf%20Sinopoli.gif?raw=true")

    st.markdown('<div class="sticker-container">', unsafe_allow_html=True)
    # URLs for the sticker images
    coffee_sticker_1 = "https://raw.githubusercontent.com/maricielonavarro31-ops/streamlit-example/9a3600dd37ff19065a5ee3916ca944020fe1d49d/cafe-shop-building-estilo-plano_156780-12.jpg"
    dessert_sticker_1 = "https://images.unsplash.com/photo-1558296316-c737c35f928e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwzNjVjNTN8MHwxfGFsbHx8fHx8fHwxfDE2NzYwNDM1MDE&ixlib=rb-4.0.3&q=80&w=400"
    coffee_sticker_2 = "https://images.unsplash.com/photo-1509042239860-f550ce7103fa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwzNjVjNTN8MHwxfGFsbHx8fHx8fHwxfDE2NzYwNDM1MDQ&ixlib=rb-4.0.3&q=80&w=400"
    dessert_sticker_2 = "https://images.unsplash.com/photo-1533602187313-2d574d6c413b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwzNjVjNTN8MHwxfGFsbHx8fHx8fHwxfDE2NzYwNDM1MDY&ixlib=rb-4.0.3&q=80&w=400"

    # Embed images with the 'sticker' class using st.markdown
    st.markdown(f'''
    <img src="{coffee_sticker_1}" alt="Coffee Sticker" class="sticker">
    <img src="{dessert_sticker_1}" alt="Dessert Sticker" class="sticker">
    <img src="{coffee_sticker_2}" alt="Another Coffee Sticker" class="sticker">
    <img src="{dessert_sticker_2}" alt="Another Dessert Sticker" class="sticker">
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Close sticker-container div
    st.markdown('</div>', unsafe_allow_html=True) # Close content-box div
