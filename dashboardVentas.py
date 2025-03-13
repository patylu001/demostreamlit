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
  # Filtros
  region_filter = st.selectbox("Selecciona una región:", df['Region'].unique())
  state_filter = st.selectbox("Selecciona un estado:", df['State'].unique())


# Aplica los filtros
filtered_df = df[(df['Region'] == region_filter) & (df['State'] == state_filter)]
# Gráfica de pastel
fig = px.pie(filtered_df, names='Category', title='Distribución por Categoría')
st.plotly_chart(fig)
# Muestra el resultado (solo la primera fila si hay resultados)
if not filtered_df.empty:
    st.write("Resultado:")
    st.dataframe(filtered_df) # Muestra la primera fila del dataframe filtrado
else:
    st.write("No se encontraron datos que coincidan con los filtros seleccionados.")
