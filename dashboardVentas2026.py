import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Added for log transformation

st.set_page_config(layout='wide')

st.title('Sales Dashboard')

# Assuming df is already loaded in the Colab environment
# To make this standalone, you might need to load the data here:
file_path="datos/SalidaVentas.xlsx"
df = pd.read_excel(file_path)

# --- Data Cleaning and Preparation (if necessary, for the dashboard context) ---
# Convert 'Order Date' to datetime for time series analysis
df['Order Date'] = pd.to_datetime(df['Order Date'])

# --- Sidebar for Filters ---
st.sidebar.header('Filtros')

# Region filter
selected_regions = st.sidebar.multiselect(
    'Selecciona la Región',
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Category filter
selected_categories = st.sidebar.multiselect(
    'Selecciona la Categoría',
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Date range filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
date_range = st.sidebar.date_input(
    'Selecciona el Rango de Fechas',
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Ensure date_range has two dates before filtering
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    filtered_df = df[
        (df['Region'].isin(selected_regions)) &
        (df['Category'].isin(selected_categories)) &
        (df['Order Date'] >= start_date) &
        (df['Order Date'] <= end_date)
    ]
else:
    filtered_df = df[
        (df['Region'].isin(selected_regions)) &
        (df['Category'].isin(selected_categories))
    ]

# Display message if no data is available after filtering
if filtered_df.empty:
    st.warning('No hay datos disponibles para la selección actual de filtros.')
else:
    # --- Key Performance Indicators (KPIs) ---
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_quantity = filtered_df['Quantity'].sum()

    st.subheader('Indicadores Clave de Desempeño (KPIs)')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Ventas Totales', value=f'${total_sales:,.2f}')
    with col2:
        st.metric(label='Ganancia Total', value=f'${total_profit:,.2f}')
    with col3:
        st.metric(label='Cantidad Total de Productos', value=f'{total_quantity:,}')

    st.markdown('---')

    # --- Sales and Profit Over Time ---
    st.subheader('Ventas y Ganancias a lo Largo del Tiempo')
    sales_profit_over_time = filtered_df.groupby('Order Date')[['Sales', 'Profit']].sum().reset_index()
    fig_time = px.line(sales_profit_over_time, x='Order Date', y=['Sales', 'Profit'],
                       title='Ventas y Ganancias Diarias',
                       labels={'value': 'Monto', 'Order Date': 'Fecha del Pedido'})
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown('---')


    # --- Sales by Region ---
    st.subheader('Ventas por Región')
    sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    fig_region = px.bar(sales_by_region, x='Region', y='Sales', title='Ventas Totales por Región',
                        labels={'Sales': 'Ventas Totales', 'Region': 'Región'}, color='Region')
    st.plotly_chart(fig_region, use_container_width=True)

    st.markdown('---')

    # --- Top 10 Products by Sales ---
    st.subheader('Top 10 Productos por Ventas')
    top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
    fig_products = px.bar(top_products, x='Sales', y='Product Name', orientation='h',
                          title='Top 10 Productos Más Vendidos',
                          labels={'Sales': 'Ventas Totales', 'Product Name': 'Nombre del Producto'})
    st.plotly_chart(fig_products, use_container_width=True)

    st.markdown('---')

    # --- Sales by State Map ---
    st.subheader('Ventas por Estado (USA)')

    # Define state abbreviations within the script for standalone execution
    state_abbreviations = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
        'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
        'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
        'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
        'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
        'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    sales_by_state = filtered_df.groupby('State')['Sales'].sum().reset_index()
    sales_by_state['State_Code'] = sales_by_state['State'].map(state_abbreviations)

    # Apply logarithmic transformation for better color distribution
    sales_by_state['Log_Sales'] = np.log1p(sales_by_state['Sales']) # log1p(x) computes log(1+x)

    fig_state = px.choropleth(
        sales_by_state,
        locations='State_Code', # Use the new 'State_Code' column for locations
        locationmode='USA-states',
        color='Log_Sales', # Use the log-transformed column for color mapping
        scope='usa',
        color_continuous_scale='Plasma', # Changed color scale to 'Plasma' for better contrast
        title='Ventas Totales por Estado en USA (Escala Logarítmica)',
        labels={'Log_Sales': 'Log de Ventas Totales', 'State': 'Estado'},
        hover_name='State', # Display original state name on hover
        hover_data={'Sales': ':.2f', 'Log_Sales': False} # Display original sales value on hover, hide log_sales
    )
    fig_state.update_layout(geo_scope='usa') # Ensures the map is centered on USA
    st.plotly_chart(fig_state, use_container_width=True)
    st.markdown('---')
