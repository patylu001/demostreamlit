import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np  # Added for log transformation

st.set_page_config(layout='wide')

st.title('Sales Dashboard')

# Assuming df is already loaded in the Colab environment
# To make this standalone, you might need to load the data here:
file_path = "datos/SalidaVentas.xlsx"
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
    def sparkline_svg(values, color):
        values = pd.Series(values).dropna()
        if values.empty:
            return ""

        min_v = values.min()
        max_v = values.max()
        if max_v == min_v:
            max_v = min_v + 1

        points = []
        for idx, val in enumerate(values):
            x = (idx / max(len(values) - 1, 1)) * 100
            y = 100 - ((val - min_v) / (max_v - min_v)) * 64 - 18
            points.append(f"{x:.2f},{y:.2f}")

        polyline = " ".join(points)
        return f'''
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:52px; display:block;">
            <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline>
        </svg>
        '''

    def pct_change(current, previous):
        if pd.isna(previous) or previous == 0:
            return 0.0 if current == 0 else 100.0
        return ((current - previous) / abs(previous)) * 100

    def render_kpi_card(title, value, delta, series, color):
        delta_class = 'positive' if delta >= 0 else 'negative'
        delta_text = f"{delta:+.1f}%"

        st.markdown(
            f'''
            <style>
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(250px, 1fr));
                    gap: 1.2rem;
                    width: 100%;
                    margin: 1rem 0 1.5rem 0;
                    align-items: stretch;
                }}
                .kpi-card {{
                    background: rgba(255,255,255,0.7);
                    border: 1px solid rgba(49, 51, 63, 0.12);
                    border-radius: 0.95rem;
                    padding: 1rem 1rem 0.9rem 1rem;
                    min-height: 330px;
                    max-width: 360px;
                    width: 100%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    overflow: visible;
                }}
                .kpi-header {{
                    font-size: 0.8rem;
                    color: rgba(49, 51, 63, 0.7);
                    line-height: 1.2;
                    margin-bottom: 0.25rem;
                }}
                .kpi-title {{
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0.2rem 0 0.5rem 0;
                    line-height: 1.1;
                }}
                .kpi-value {{
                    font-size: clamp(2.5rem, 2vw, 4.5rem);
                    font-weight: 800;
                    line-height: 0.9;
                    letter-spacing: -0.05em;
                    color: #111827;
                    margin: 0.1rem 0 0.4rem 0;
                    display: block;
                    white-space: normal;
                }}
                .kpi-sparkline {{
                    width: 100%;
                    height: 52px;
                    margin-top: 0.45rem;
                    margin-bottom: 0.15rem;
                    display: flex;
                    align-items: flex-end;
                }}
                .kpi-footer {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-top: auto;
                    padding-top: 0.7rem;
                    border-top: 1px solid rgba(49,51,63,0.08);
                    font-size: 0.82rem;
                    color: rgba(49, 51, 63, 0.8);
                    min-height: 28px;
                }}
                .kpi-delta {{
                    font-weight: 700;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.25rem;
                }}
                .kpi-delta.positive {{ color: #2ea76a; }}
                .kpi-delta.negative {{ color: #e75a4f; }}
                @media (max-width: 1000px) {{
                    .kpi-grid {{ grid-template-columns: 1fr; }}
                    .kpi-card {{ max-width: 100%; }}
                }}
            </style>
            ''',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'''
            <div class="kpi-card">
                <div>
                    <div class="kpi-header">Month to date</div>
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                <div class="kpi-sparkline">{sparkline_svg(series, color)}</div>
                <div class="kpi-footer">
                    <div>{'Stripe' if 'Ventas' in title or 'Ganancia' in title else 'Total'}</div>
                    <div class="kpi-delta {delta_class}">{delta_text}</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_quantity = filtered_df['Quantity'].sum()

    daily_sales = filtered_df.sort_values('Order Date').set_index('Order Date')['Sales'].resample('D').sum().fillna(0)
    daily_profit = filtered_df.sort_values('Order Date').set_index('Order Date')['Profit'].resample('D').sum().fillna(0)
    daily_quantity = filtered_df.sort_values('Order Date').set_index('Order Date')['Quantity'].resample('D').sum().fillna(0)

    sales_series = daily_sales.tail(14).tolist()
    profit_series = daily_profit.tail(14).tolist()
    quantity_series = daily_quantity.tail(14).tolist()

    sales_delta = pct_change(sales_series[-1], np.mean(sales_series[:-1]) if len(sales_series) > 1 else 0)
    profit_delta = pct_change(profit_series[-1], np.mean(profit_series[:-1]) if len(profit_series) > 1 else 0)
    quantity_delta = pct_change(quantity_series[-1], np.mean(quantity_series[:-1]) if len(quantity_series) > 1 else 0)

    cards = [
        ("Revenue", f'${total_sales:,.0f}', sales_delta, sales_series, '#5CC68A'),
        ("Profit", f'${total_profit:,.0f}', profit_delta, profit_series, '#5CC68A'),
        ("Units", f'{total_quantity:,.0f}', quantity_delta, quantity_series, '#5CC68A'),
    ]

    cols = st.columns(3)
    for col, (title, value, delta, series, color) in zip(cols, cards):
        with col:
            render_kpi_card(title, value, delta, series, color)

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
    sales_by_state['Log_Sales'] = np.log1p(sales_by_state['Sales'])  # log1p(x) computes log(1+x)

    fig_state = px.choropleth(
        sales_by_state,
        locations='State_Code',  # Use the new 'State_Code' column for locations
        locationmode='USA-states',
        color='Log_Sales',  # Use the log-transformed column for color mapping
        scope='usa',
        color_continuous_scale='Plasma',  # Changed color scale to 'Plasma' for better contrast
        title='Ventas Totales por Estado en USA (Escala Logarítmica)',
        labels={'Log_Sales': 'Log de Ventas Totales', 'State': 'Estado'},
        hover_name='State',  # Display original state name on hover
        hover_data={'Sales': ':.2f', 'Log_Sales': False}  # Display original sales value on hover, hide log_sales
    )
    fig_state.update_layout(geo_scope='usa')  # Ensures the map is centered on USA
    st.plotly_chart(fig_state, use_container_width=True)
    st.markdown('---')
