import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Rendimiento Financiero",
    page_icon="📊",
    layout="wide"
)

# Cargar datos de manera eficiente con cache
@st.cache_data
def load_data():
    file_path = 'datos/SalidaVentas.xlsx'
    df = pd.read_excel(file_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Discount'] = df['Discount'].fillna(0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"No se pudo cargar el archivo: {e}")
    st.stop()

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard Interactivo de Ventas y Rentabilidad")
st.markdown("Analiza el rendimiento financiero, detecta fugas de dinero y evalúa el impacto de los descuentos.")

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Búsqueda")

# Filtro de Región
regiones = st.sidebar.multiselect("Selecciona Región(es)", options=df['Region'].unique(), default=df['Region'].unique())
filtered_df = df[df['Region'].isin(regiones)]

# Filtro de Estado (dinámico según región)
estados_disponibles = filtered_df['State'].unique()
estados = st.sidebar.multiselect("Selecciona Estado(s)", options=estados_disponibles, default=estados_disponibles)
filtered_df = filtered_df[filtered_df['State'].isin(estados)]

# Filtro de Categoría
categorias = st.sidebar.multiselect("Selecciona Categoría(s)", options=df['Category'].unique(), default=df['Category'].unique())
filtered_df = filtered_df[filtered_df['Category'].isin(categorias)]

# --- TABS DEL DASHBOARD ---
tab_principal, tab_mapa = st.tabs(["Dashboard principal", "Ventas por Estado"])

with tab_principal:
    # --- MÉTRICAS CLAVE (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric("Ventas Totales", f"${total_sales:,.2f}")

    with col2:
        total_profit = filtered_df['Profit'].sum()
        delta_color = "normal" if total_profit >= 0 else "inverse"
        st.metric("Beneficio Total (Profit)", f"${total_profit:,.2f}", delta_color=delta_color)

    with col3:
        avg_discount = filtered_df['Discount'].mean() * 100
        st.metric("Descuento Promedio", f"{avg_discount:.1f}%")

    with col4:
        total_orders = filtered_df['Order ID-1'].nunique()
        st.metric("Órdenes Únicas", f"{total_orders:,}")

    # --- GRÁFICOS PRINCIPALES ---
    st.markdown("--- ")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Rentabilidad por Estado")
        profit_state = filtered_df.groupby('State')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False)
        fig_state = px.bar(
            profit_state,
            x='Profit',
            y='State',
            orientation='h',
            title="Beneficios por Estado",
            color='Profit',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_state, width='stretch')

    with col_right:
        st.subheader("Relación Descuento vs. Beneficios")
        fig_scatter = px.scatter(
            filtered_df,
            x='Discount',
            y='Profit',
            color='Category',
            hover_data=['Sub-Category', 'Sales'],
            title="Impacto del Descuento en la Ganancia"
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_scatter, width='stretch')

    # --- DETALLE DE SUB-CATEGORÍAS AFECTADAS ---
    st.subheader("Análisis de Desempeño por Sub-Categoría")
    sub_analysis = filtered_df.groupby('Sub-Category').agg(
        Ventas=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Descuento_Promedio=('Discount', lambda x: f"{x.mean()*100:.1f}%")
    ).reset_index().sort_values(by='Profit')

    # Resaltar filas con pérdidas utilizando estilos de pandas
    def color_negative_red(val):
        color = 'red' if val < 0 else 'black'
        return f'color: {color}'

    st.dataframe(
        sub_analysis.style.map(color_negative_red, subset=['Profit']),
        width='stretch'
    )

with tab_mapa:
    st.subheader("Mapa de ventas por estado")

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

    sales_by_state = (
        filtered_df.groupby('State', dropna=False)['Sales']
        .sum()
        .reset_index()
        .rename(columns={'Sales': 'Ventas'})
    )

    sales_by_state['State_Code'] = sales_by_state['State'].map(state_abbreviations)
    sales_by_state = sales_by_state.dropna(subset=['State_Code']).sort_values('Ventas', ascending=False)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Ventas totales', f"${sales_by_state['Ventas'].sum():,.0f}")
    with col2:
        st.metric('Estado con más ventas', sales_by_state.iloc[0]['State'] if not sales_by_state.empty else 'N/A')
    with col3:
        st.metric('Máximo valor', f"${sales_by_state['Ventas'].max():,.0f}")

    fig_map = px.choropleth(
        sales_by_state,
        locations='State_Code',
        locationmode='USA-states',
        color='Ventas',
        scope='usa',
        color_continuous_scale='Plasma',
        range_color=(sales_by_state['Ventas'].min(), sales_by_state['Ventas'].max()),
        labels={'Ventas': 'Ventas', 'State': 'Estado'},
        hover_name='State',
        hover_data={'State_Code': False, 'Ventas': ':,.2f'},
        title='Ventas Totales por Estado',
    )
    fig_map.update_layout(
        template='plotly_white',
        geo=dict(scope='usa', lakecolor='white'),
        margin=dict(l=0, r=0, t=40, b=0),
        height=650,
    )
    st.plotly_chart(fig_map, width='stretch')

    st.dataframe(
        sales_by_state[['State', 'Ventas']].sort_values('Ventas', ascending=False).reset_index(drop=True),
        width='stretch'
    )
