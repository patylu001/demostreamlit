import streamlit as st
import pandas as pd
import plotly.express as px

#Título
st.title("Mi primer app de streamlit editada")

#Para ejecutar, desde la consola escribimos: streamlit run nombrearhivo.py

#header
st.header("Semestre Sep-Enero 2021")

#Texto
st.text("Herramientas para el análisis de datos")

#Markdown
st.markdown("### Hola")

#Mensajes

st.success("Successful")

st.info("Information!")

st.warning("This is a warning")

st.error("This is an error Danger")

st.text("Lo interesante de streamlit son los widgets:")

valor = st.checkbox("Show/Hide")
# Checkbox
if valor:
    st.text("Showing or Hiding Widget")

# Radio Buttons
status = st.radio("What is your status", ("Active", "Inactive"))

if status == 'Active':
    st.success("You are Active")
else:
    st.warning("Inactive, Activate")

# SelectBox
occupation = st.selectbox(
    "Your Occupation",
    ["Programmer", "DataScientist", "Doctor", "Businessman"])
st.write("You selected this option ", occupation)

# MultiSelect
location = st.multiselect("Where do you work?",
                          ("London", "New York", "Accra", "Kiev", "Nepal"))
st.write("You selected", len(location), "locations")

# Slider
level = st.slider("What is your level", 1, 5)

# Buttons
st.button("Simple Button")

if st.button("About"):
    st.text("Streamlit is Cool")

# SIDEBARS
st.sidebar.header("About")
st.sidebar.text("This is Streamlit Tut")


#Tambien podemos seguir llamando al código de python con el que hemos estado trabajando: pandas, plots, etc,
@st.cache  # Para que los datos solo se descarguen una vez
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)


df = get_data()

st.dataframe(df.head())

st.map(df)

values = st.sidebar.slider("Price range", float(df.price.min()), 1000.0,
                           (50.0, 300.0))
st.write(values[1])

f = px.histogram(df[(df.price > int(values[0])) & (df.price < int(values[1]))],
                 x="price",
                 nbins=15,
                 title="Price distribution")
f.update_xaxes(title="Price")
f.update_yaxes(title="No. of listings")
st.plotly_chart(f)
