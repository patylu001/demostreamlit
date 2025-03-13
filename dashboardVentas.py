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

# Crear un filtro de selección basado en la columna 'region'
region_seleccionada = st.selectbox('Selecciona una región', df['Region'].unique())

# Filtrar el dataframe basado en la selección
df_filtrado = df[df['Region'] == region_seleccionada]

# Mostrar el dataframe filtrado
st.write('Dataframe filtrado por región:', region_seleccionada)
st.dataframe(df_filtrado)
