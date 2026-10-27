import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ventas por Estado", page_icon="🗺️", layout="wide")

st.title("🗺️ Mapa de Ventas por Estado")
st.caption("Visualiza el volumen de ventas por estado usando una escala de color")


@st.cache_data
def load_data():
    file_path = "datos/SalidaVentas.xlsx"
    df = pd.read_excel(file_path)
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    return df


df = load_data()

# Filtros laterales
st.sidebar.header("Filtros")
selected_regions = st.sidebar.multiselect(
    "Selecciona la región",
    options=df["Region"].dropna().unique(),
    default=df["Region"].dropna().unique(),
)
selected_categories = st.sidebar.multiselect(
    "Selecciona la categoría",
    options=df["Category"].dropna().unique(),
    default=df["Category"].dropna().unique(),
)

filtered_df = df[
    df["Region"].isin(selected_regions) & df["Category"].isin(selected_categories)
].copy()

if filtered_df.empty:
    st.warning("No hay datos para la selección actual.")
    st.stop()

# Mapeo de estados a códigos US
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

# Agregación por estado
sales_by_state = (
    filtered_df.groupby("State", dropna=False)["Sales"]
    .sum()
    .reset_index()
    .rename(columns={"Sales": "Ventas"})
)

sales_by_state["State_Code"] = sales_by_state["State"].map(state_abbreviations)
sales_by_state = sales_by_state.dropna(subset=["State_Code"]).sort_values("Ventas", ascending=False)

# KPI resumen
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas totales", f"${sales_by_state['Ventas'].sum():,.0f}")
with col2:
    st.metric("Estado con más ventas", sales_by_state.iloc[0]["State"] if not sales_by_state.empty else "N/A")
with col3:
    st.metric("Máximo valor", f"${sales_by_state['Ventas'].max():,.0f}")

# Mapa choropleth
fig = px.choropleth(
    sales_by_state,
    locations="State_Code",
    locationmode="USA-states",
    color="Ventas",
    scope="usa",
    color_continuous_scale="Plasma",
    range_color=(sales_by_state["Ventas"].min(), sales_by_state["Ventas"].max()),
    labels={"Ventas": "Ventas", "State": "Estado"},
    hover_name="State",
    hover_data={"State_Code": False, "Ventas": ":,.2f"},
    title="Ventas Totales por Estado",
)

fig.update_layout(
    template="plotly_white",
    geo=dict(scope="usa", lakecolor="white"),
    margin=dict(l=0, r=0, t=40, b=0),
    height=650,
)

st.plotly_chart(fig, use_container_width=True)

# Top 10 estados con mayor venta
st.subheader("Top 10 estados con más ventas")

bar_data = sales_by_state.head(10).sort_values("Ventas", ascending=True).copy()
bar_data["Ventas_Formateado"] = bar_data["Ventas"].map(lambda x: f"${x:,.0f}")

fig_bar = px.bar(
    bar_data,
    x="Ventas",
    y="State",
    orientation="h",
    color="Ventas",
    color_continuous_scale="Viridis",
    text=bar_data["Ventas_Formateado"],
    title="Los 10 estados con mayor volumen de ventas",
)

fig_bar.update_traces(textposition="outside", cliponaxis=False)
fig_bar.update_layout(
    template="plotly_white",
    height=500,
    margin=dict(l=10, r=20, t=40, b=10),
    xaxis_title="Ventas",
    yaxis_title="Estado",
    coloraxis_showscale=False,
)

st.plotly_chart(fig_bar, use_container_width=True)

# Tabla de resumen
st.subheader("Resumen por estado")
st.dataframe(
    sales_by_state[["State", "Ventas"]].sort_values("Ventas", ascending=False).reset_index(drop=True),
    use_container_width=True,
)
