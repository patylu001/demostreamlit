import pandas as pd
import streamlit as st
import plotly.express as px

# Lee el archivo Excel
try:
  df = pd.read_excel('SalidaFinal.xlsx')
  print(df.head())  # Muestra las primeras filas del DataFrame
except FileNotFoundError:
  print("Error: El archivo 'SalidaFinal.xlsx' no se encuentra.")
except Exception as e:
  print(f"Error al leer el archivo: {e}")



# Lee el archivo Excel
try:
    # Agrupa por región y suma las ventas
    sales_by_region = df.groupby('Region')['Sales'].sum()

    # Crea la gráfica de barras con Plotly Express
    fig = px.bar(sales_by_region, 
                 x=sales_by_region.index, 
                 y='Sales', 
                 title='Ventas Acumuladas por Región',
                 labels={'Sales': 'Ventas', 'x': 'Región'})
    
    st.plotly_chart(fig)

except FileNotFoundError:
    st.error("Error: El archivo 'SalidaFinal.xlsx' no se encuentra.")
except Exception as e:
    st.error(f"Error al leer el archivo o generar la gráfica: {e}")
with st.sidebar:
# Aplica los filtros
# Filtro para la columna "Region"
  region_filter = st.selectbox("Selecciona una región:", df['Region'].unique())
  df_filtered = df[df['Region'] == region_filter]

# Segundo filtro para la columna "State" basado en el filtro de "Region"
  state_filter = st.selectbox("Selecciona un estado:", df_filtered['State'].unique())
  df_filtered = df_filtered[df_filtered['State'] == state_filter]




# Muestra el DataFrame filtrado
st.dataframe(df_filtered)

# Gráfica de pastel para la columna "Category"
category_counts = df_filtered['Category'].value_counts()
fig_pie = px.pie(category_counts, 
                     values=category_counts.values, 
                     names=category_counts.index, 
                     title='Distribución de Categorías')
st.plotly_chart(fig_pie)
